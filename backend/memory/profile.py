from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime, timezone
from langchain_core.prompts import ChatPromptTemplate
from supabase import Client
import logging
from langchain_core.output_parsers import StrOutputParser

# ==============================
# 1️ Prompt（结构化 + 推理）
# ==============================
profile_prompt = ChatPromptTemplate.from_messages([
    ("system", """
    你是一个高级用户画像系统，需要：

    1. 提取用户明确表达的信息
    2. 推理隐含信息（非常重要）
    3. 不要删除已有信息
    4. 输出必须符合 schema

    推理规则：
    - 经常做某事 → 兴趣
    - 多次提到 → 提高权重
    - 行为 → 性格

    例如：
    打篮球 → hobbies + preferences
    """),
    ("human", "已有画像：{profile}\n新对话：{message}")
])


# ==============================
# 2️ Schema（Pydantic v2 标准）
# ==============================
class UserProfile(BaseModel):
    """
    用户画像结构（强约束）
    """

    name: Optional[str] = None
    age: Optional[int] = None
    # 兴趣列表（避免共享引用）
    hobbies: List[str] = Field(default_factory=list)
    # 偏好（带权重）
    preferences: Dict[str, float] = Field(default_factory=dict)
    # 性格特征
    personality: List[str] = Field(default_factory=list)
    # 更新时间（ISO格式字符串）
    last_updated: Optional[str] = None


# ==============================
# 3️ ProfileMemory（核心模块）
# ==============================
class ProfileMemory:
    """
    工业级用户画像管理模块
    """

    def __init__(self, user_id: str, supabase: Client, llm:ChatOpenAI):
        self.user_id = user_id
        self.supabase = supabase
        # LangChain 1.x 推荐：结构化输出
        self.structured_llm = llm.with_structured_output(UserProfile)

    # ==============================
    # 1️ 加载（DB → Pydantic）
    # ==============================
    def load(self) -> UserProfile:
        """
        从数据库加载用户画像
        """
        try:
            res = self.supabase.table("profiles") \
                .select("profile") \
                .eq("id", self.user_id) \
                .execute()

            print(f"Load profile from DB: {res}")

            if res.data and res.data[0]["profile"]:
                return UserProfile(**res.data[0]["profile"])

        except Exception as e:
            logging.error(f"Load profile error: {e}")

        return UserProfile()

    # ==============================
    # 2️ 保存（Pydantic → DB）
    # ==============================
    def save(self, profile: UserProfile):
        try:
             # Pydantic v2 推荐,将模型实例转换为字典格式
            data = profile.model_dump() 
            # 标准时间（UTC + ISO）
            data["last_updated"] = datetime.now(timezone.utc).isoformat()

            self.supabase.table("user_profile").upsert({
                "user_id": self.user_id,
                "profile": data
            }).execute()

        except Exception as e:
            logging.error(f"Save profile error: {e}")

    # ==============================
    # 3️ LLM 提取（结构化） 旧对话+新消息
    # ==============================
    def extract_profile(self, old_profile: UserProfile, message: str) -> UserProfile:
        """
        使用 LLM 提取 + 推理用户画像（结构化）
        旧对话+新消息
        输出：新画像
        """

        chain = profile_prompt | self.structured_llm

        try:
            new_profile = chain.invoke({
                "profile": old_profile.model_dump(),
                "message": message
            })
            print(new_profile)
            print(StrOutputParser().parse(new_profile))

            return new_profile

        except Exception as e:
            logging.error(f"LLM extract error: {e}")
            return old_profile

    # ==============================
    # 4️ merge（核心逻辑）
    # ==============================
    def merge(self, old: UserProfile, new: UserProfile) -> UserProfile:
        """
        合并新旧画像（不丢数据）
        """

        data = old.model_dump()

        for key, value in new.model_dump().items():

            if value is None:
                continue

            # ========= list 合并（保序去重） =========
            if isinstance(value, list):
                existing = data.get(key, [])
                merged = []

                for item in existing + value:
                    if item not in merged:
                        merged.append(item)

                data[key] = merged

            # ========= dict 合并（偏好） =========
            elif isinstance(value, dict):
                merged = data.get(key, {}).copy()

                for k, v in value.items():
                    # 保留更高权重
                    merged[k] = max(merged.get(k, 0), v)

                data[key] = merged

            # ========= 普通字段 =========
            else:
                data[key] = value


        return UserProfile(**data)

    # ==============================
    # 5️ 外部统一入口（核心逻辑）
    # ==============================
    def update(self, message: str) -> UserProfile:
        """
        完整流程：
        load → extract → merge → save
        读取旧画像 =>  旧画像 + 新对话 LLM 提取 + 推理 => 合并新旧画像 => 保存新画像
        """

        # 1️ 读取旧画像
        old_profile = self.load()

        # 2️ LLM 提取 + 推理               
        new_profile = self.extract_profile(old_profile, message)

        # 3️ 合并
        merged_profile = self.merge(old_profile, new_profile)

        # 4️ 保存
        self.save(merged_profile)

        print(f"Update profile: {merged_profile}")

        return merged_profile
