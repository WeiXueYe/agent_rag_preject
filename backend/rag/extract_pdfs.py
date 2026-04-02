from fastapi import UploadFile
import docx
from langchain_community.embeddings import DashScopeEmbeddings
import os
from dotenv import load_dotenv
from supabase import Client


load_dotenv()


def sliding_window_chunking(text, window_size=512, step_size=256):
    """滑动窗口切片"""
    chunks = []
    for i in range(0, len(text), step_size):
        chunk = text[i:i + window_size]
        
        if len(chunk.strip()) > 0:
            chunks.append(chunk.strip())
    
    return chunks


embeddings = DashScopeEmbeddings(
    model=os.getenv("DASHSCOPE_EMBEDDING_MODEL"),  # 指定你想要的版本
    dashscope_api_key=os.getenv("DASHSCOPE_API_KEY")  # 或者设置环境变量 DASHSCOPE_API_KEY
)


from PyPDF2 import PdfReader
from langchain import chains
from langchain_community.callbacks import get_openai_callback
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.vectorstores import FAISS
from typing import List, Tuple
import os
import pickle

DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY')
if not DASHSCOPE_API_KEY:
    raise ValueError("请设置环境变量 DASHSCOPE_API_KEY")

def extract_text_with_page_numbers(pdf) -> Tuple[str, List[int]]:
    """
    从PDF中提取文本并记录每行文本对应的页码
    
    参数:
        pdf: PDF文件对象
    
    返回:
        text: 提取的文本内容
        page_numbers: 每行文本对应的页码列表
    """
    text = ""
    page_numbers = []

    for page_number, page in enumerate(pdf.pages, start=1):
        extracted_text = page.extract_text()
        if extracted_text:
            text += extracted_text
            page_numbers.extend([page_number] * len(extracted_text.split("\n")))

    return text, page_numbers




def extract_pdfs(file: UploadFile,inserted_id: int,supabase: Client,agent_id: int):
    """从PDF文件中提取文本并切片"""

    try:
        # 读取PDF文件
        pdf = PdfReader(file.file)
        
        # 提取文本
        text, _ = extract_text_with_page_numbers(pdf)
        
        # 使用滑动窗口切片
        chunks = sliding_window_chunking(text)

        for content in chunks:
            embedding = embeddings.embed_query(content)
            supabase.table("rag_vec").insert({
                "agent_id":int(agent_id),
                "file_id": inserted_id,
                "content": content,
                "vec": embedding
            }).execute()

        return chunks
    except Exception as e:
        print(f"处理PDF文件时出错: {str(e)}")
        return []