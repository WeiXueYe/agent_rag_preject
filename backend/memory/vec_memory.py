from postgrest import APIError
from supabase import Client
import os
import uuid
import json
from supabase import create_client
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

# ==============================
# 3️ Vector Memory（向量记忆）
# ==============================

class VectorMemory:
    """
    存储“原始对话片段”，用于语义检索
    表: memory_vectors  
    """

    def __init__(self, 
                 user_id: uuid.UUID, 
                 agent_id: int, 
                 supabase: Client, 
                 llm: ChatOpenAI, 
                 embeddings: DashScopeEmbeddings):
        self.user_id = user_id
        self.agent_id = agent_id
        self.supabase = supabase
        self.llm = llm
        self.embeddings = embeddings


    def calc_importance(self, text: str) -> float:
        prompt = f"""
        你是一个信息重要性评估专家。请评估以下内容的重要性并返回0到1之间的浮点数。

        ## 评估维度：
        
        1. **持久性**：信息是长期有效(1.0)还是临时性(0.0)？
        2. **个人相关性**：与个人身份/偏好高度相关(1.0)还是无关(0.0)？
        3. **实用价值**：对未来互动有实际帮助(1.0)还是无帮助(0.0)？
        4. **独特性**：独特重要信息(1.0)还是常见废话(0.0)？

        ## 评分标准：

        **重要信息 (0.7-1.0)：**
        - 个人身份信息：姓名、生日、职业、住址、联系方式等
        - 长期偏好与习惯：饮食偏好、兴趣爱好、生活习惯、价值观等
        - 重要人际关系：家庭成员、朋友、重要纪念日等
        - 具体需求与目标：工作任务、学习计划、购物清单等
        - 健康与安全相关：过敏信息、疾病史、紧急联系方式等
        - 重要决策与承诺：约定、承诺、重要选择等

        **中等重要 (0.4-0.6)：**
        - 一般性话题讨论：新闻、观点、知识分享
        - 短期计划：当天的安排、临时活动
        - 情感表达但不涉及深层信息
        - 模糊的需求表达

        **不重要 (0.0-0.3)：**
        - 寒暄问候：你好、在吗、怎么样等
        - 无实质内容的回应：嗯、哦、好的等
        - 纯粹的感叹词：哇、啊等
        - 重复已确认的信息
        - 与个人无关的随机信息

        ## 评分示例：
        - "我叫张三，生日是1990年5月1日" → 0.95
        - "我有一个儿子，今年5岁了" → 0.85
        - "我不喜欢吃辣" → 0.75
        - "明天下午3点开会" → 0.65
        - "今天天气真不错" → 0.35
        - "你好" → 0.1
        - "嗯嗯" → 0.05

        ## 待评估内容：
        {text}

        ## 要求：
        - 仅返回一个0到1之间的浮点数，精确到小数点后两位
        - 不要有任何解释或额外文字
        - 根据上述标准合理评分
        """
        
        score = self.llm.invoke(prompt).content.strip()
        try:
            return float(score)
        except:
            return 0.5

    def add(self, text: str):
        """
        存储一条记忆(embedding + text)
        """
        print(f"添加记忆：{text}")

        embedding = self.embeddings.embed_query(text)
        print("embedding OK")
        importance = self.calc_importance(text)
        print(f"importance OK: {importance}")

        if importance > 0.3:
            try:
                self.supabase.table("memory_vec").insert({
                    "belong_user_id": str(self.user_id), 
                    "belong_agent_id": int(self.agent_id),
                    "content": str(text),
                    "embedding": embedding, 
                    "importance": float(importance),
                    "access_count": 0,
                    "last_access": "now()" 
                }).execute()
            except APIError as e:
                print(f"错误代码: {e.code}")
                print(f"详细信息: {e.message}") 
                print(f"提示: {e.hint}")

        return importance


    def search(self, query: str, k: int = 3):
        """
        从数据库中检索最相关的记忆
        依赖 Supabase RPC: match_memory
        """
        query_embedding = self.embeddings.embed_query(query)

        res = self.supabase.rpc("match_memory", {
            "query_embedding": query_embedding,
            "match_count": k,
            "user_id": self.user_id,
            "agent_id": self.agent_id,
        }).execute()

        results = res.data

        for r in results:
            self.supabase.table("memory_vec").update({
                "access_count": r.get("access_count", 0) + 1,
                "last_access": "now()"
            }).eq("content", r["content"]).execute()
        # rpc函数结构化返回值
        return [r["content"] for r in results]