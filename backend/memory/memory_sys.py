from psutil import users
from supabase import Client
from dotenv import load_dotenv
import os
from supabase import create_client
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from memory.profile import ProfileMemory, UserProfile
from memory.recent_memory import RecentMemory
from memory.vec_memory import VectorMemory
from rag.search_similar_content import search_similar_content


load_dotenv()

#  LLM 和 embedding
llm = ChatOpenAI(
    model=os.getenv("DASHSCOPE_MODEL"), 
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key=os.getenv("DASHSCOPE_API_KEY")
)
embeddings = DashScopeEmbeddings(
    model=os.getenv("DASHSCOPE_EMBEDDING_MODEL"),  # 指定你想要的版本
    dashscope_api_key=os.getenv("DASHSCOPE_API_KEY")  # 或者设置环境变量 DASHSCOPE_API_KEY
)

# 主对话 Prompt（融合三层记忆）
chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个智能助手"),
    ("system", "【用户画像】\n{profile}"),
    ("system", "【相关记忆】\n{vmemory}"),
    ("system", "【相关知识】\n{file_content}"),
    ("system", "【最近对话】\n{recent}"),
    ("system", "【用户设置】\n{userprompt}"),
    ("human", "{input}")
])


# 拆分句子 Prompt
split_prompt = ChatPromptTemplate.from_messages([
    ("system","""
    你是一个专业的句子拆分助手，一段句子中可能既有事实，也有偏好，你需要把句子拆成独立的事实或偏好片段。
     你的任务是把句子拆成独立的事实或偏好片段，每个片段保持完整意义。

    ## 评估准则：
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
    
    ## 示例：
     
    请把下面句子拆成独立的事实或偏好片段，每个片段保持完整意义：

    ### 文本：我喜欢篮球但是今天很无聊，我昨天还看了电影

    ### 输出：
    1. 我喜欢篮球
    2. 我今天很无聊
    3. 我昨天看了电影
     
    ### 格式：
    一个JSON 格式的字符串列表，每个字符串是一个独立的事实或偏好片段，每个片段保持完整意义。
    例如：
    ["我喜欢篮球", "我今天很无聊", "我昨天看了电影"]
    """
     ),
    ("human", "{input}")
])


class MemoryChatSystem:

    def __init__(self, user_id: str, agent_id: int, supabase: Client):
        self.user_id = user_id
        self.agent_id = agent_id
        self.supabase = supabase
        # 向量记忆
        self.vector_memory = VectorMemory(user_id,agent_id,supabase,llm,embeddings)
        # 短期记忆 Redis
        self.recent_memory = RecentMemory(user_id,agent_id)
        # 用户画像
        self.profile_memory = ProfileMemory(user_id,supabase,llm) 

    def split_sentence(self, sentence: str) -> list[str]:
        """
        拆分句子
        """
        parser = JsonOutputParser()
        chain = split_prompt | llm | parser
        res = chain.invoke({"input": sentence})
        return res

    def chat(self, user_input: str) -> str:
        """
        一次完整对话流程
        """

        # 获取相关变量
        vmemories = self.vector_memory.search(user_input)
        # 获取最近对话
        recent = self.recent_memory.get_recent()
        # 获取用户画像
        profile = self.profile_memory.load()
        # 获取用户设置
        user_prompt_res = self.supabase.table("agent")\
            .select("prompt")\
            .eq("id", self.agent_id)\
            .execute()

        if user_prompt_res.data and len(user_prompt_res.data) > 0:
            userprompt = user_prompt_res.data[0]["prompt"]
        else: 
            userprompt = "默认提示词" 
        
        file_content = search_similar_content(
            embeddings.embed_query(user_input),
            self.agent_id,
            self.supabase)

        # 构建chain
        chain = chat_prompt | llm | StrOutputParser()

        ai_output = chain.invoke({
            "input": user_input,
            "vmemory": "\n".join(vmemories),
            "recent": recent,
            "profile": profile.model_dump(),
            "userprompt": userprompt,
            "file_content": file_content
            })


        try:
            sentences = self.split_sentence(user_input)
            # print(type(sentences))
            # print(sentences)
            for sentence in sentences:
                importance = self.vector_memory.add(f"用户: {sentence}")
                # print(f"句子：{sentence}")
                # print(f"消息的重要性：{importance}")
                if importance > 0.5:
                    self.profile_memory.update(f"用户:{sentence}")
        except:
            print("拆分句子失败")
            importance = self.vector_memory.add(f"用户:{user_input} AI:{ai_output}")

        # 更新对话计录
        self.recent_memory.save_message(user_input, ai_output)

        return ai_output
    

    def get_history(self,user_input: str) -> str:
        """
        获取用户最近对话
        """
        # 获取相关变量
        vmemories = self.vector_memory.search(user_input)
        # 获取最近对话
        recent = self.recent_memory.get_recent()
        # 获取用户画像
        profile = self.profile_memory.load()

        template = """
        ### 用户背景信息
        {profile}

        ### 相关历史记忆 (RAG)
        {vmemory}

        ### 最近几轮对话回放
        {recent}
            """

        res_prompt = template.format(
            profile=profile.model_dump(),
            vmemory="\n".join(vmemories),
            recent=recent
        )

        return res_prompt
    
    def save_chat(self, user_input: str, ai_output: str):
        """
        保存对话
        """
        try:
            sentences = self.split_sentence(user_input)
            # print(type(sentences))
            # print(sentences)
            for sentence in sentences:
                importance = self.vector_memory.add(f"用户: {sentence}")
                # print(f"句子：{sentence}")
                # print(f"消息的重要性：{importance}")
                if importance > 0.5:
                    self.profile_memory.update(f"用户:{sentence}")
        except:
            print("拆分句子失败")
            importance = self.vector_memory.add(f"用户:{user_input} AI:{ai_output}")

        # 更新对话计录
        self.recent_memory.save_message(user_input, ai_output)