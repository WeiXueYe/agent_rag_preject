from tools.translate import tencent_translate
import os
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
# Supabase 相关
from supabase import ClientOptions, create_client
from langchain.agents import create_agent
# LangChain 核心
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_community.utilities import SerpAPIWrapper
from langchain_core.tools import Tool

# 你的自定义模块 (请确保路径正确)
from memory.memory_sys import MemoryChatSystem
from auth import authenticate

# 加载环境变量
load_dotenv()

# --- 配置部分 ---
API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")
MODEL_NAME = os.environ.get("DASHSCOPE_MODEL", "qwen-turbo")
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

serp_search = SerpAPIWrapper()

search_tool = Tool(
    name="Intermediate Answer",  # Agent 内部识别的名称
    func=serp_search.run,             # 工具执行的函数
    description="当你想搜索互联网获取实时信息或关于当前事件的答案时非常有用。" # 提示词：告诉 LLM 什么时候用它
)

# 1. 初始化大模型 (使用 OpenAI 适配器模式对接通义千问)
llm = ChatOpenAI(
    model=MODEL_NAME, 
    base_url=BASE_URL,
    api_key=API_KEY,
    temperature=0  # Agent 通常需要较低的温度以保持逻辑稳定
)

router = APIRouter()

# --- 提示词模板：隐式思考 ---
AGENT_TMPL = """你是一个专业助手。你可以根据需要调用工具来辅助回答。

用户会输入英文内容，你必须调用工具里的tencent_translate函数，将英文内容翻译成中文
tencent_translate函数的参数为text，返回值为翻译后的中文内容

{user_prompt}

已知对话历史:
{chat_history}

"""

prompt = PromptTemplate.from_template(AGENT_TMPL)

# --- 3. 辅助函数 ---
def get_supabase_by_token(token: str):
    url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    anon_key = os.getenv("NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY")
    options = ClientOptions(headers={"Authorization": f"Bearer {token}"})
    return create_client(url, anon_key, options=options)

# 获取用户设置的提示词
def get_user_set_prompt(supabase, agent_id: int):
    user_prompt_res = supabase.table("agent")\
        .select("prompt")\
        .eq("id", agent_id)\
        .execute()
    if user_prompt_res.data and len(user_prompt_res.data) > 0:
        userprompt = user_prompt_res.data[0]["prompt"]
    else: 
        userprompt = "默认提示词" 
    return userprompt

# --- 4. 定义请求结构 ---
class ChatRequest(BaseModel):
    prompt: str
    agent_id: int

# --- 5. 路由入口 ---
@router.post("/chat")
async def chat(chat_request: ChatRequest, current_user: dict = Depends(authenticate)):
    try:
        token = current_user["token"]
        payload = current_user["payload"]
        user_id = payload["sub"]

        # 初始化带有 RLS 权限的 Supabase
        supabase = get_supabase_by_token(token)

        # 初始化你的记忆系统
        memory_chat_sys = MemoryChatSystem(
            user_id=user_id,
            agent_id=chat_request.agent_id,
            supabase=supabase,
        )
        
        # # 获取并格式化历史记录
        chat_history = memory_chat_sys.get_history(chat_request.prompt)

        # 定义工具 (可以在此处注入依赖 supabase 的工具)
        tools = [
            tencent_translate,
            search_tool,
        ]

        AGENT_TMPL = prompt.format(
            user_prompt=get_user_set_prompt(supabase, chat_request.agent_id),
            chat_history=chat_history
        )
        # 创建 Agent 运行链
        agent = create_agent(
            llm,
            tools,
            system_prompt=AGENT_TMPL
        )



        # 执行 Agent 推理
        result = agent.invoke({
            "messages": [
                {"role": "user", "content": f"{chat_request.prompt}"}
            ]
        })
        ai_output = result['messages'][-1].content

        # 异步保存对话到数据库
        memory_chat_sys.save_chat(chat_request.prompt, ai_output)

        return {
            "success": True,
            "model": MODEL_NAME,
            "response": ai_output
        }

    except Exception as e:
        print(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))