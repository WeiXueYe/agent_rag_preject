from fastapi import UploadFile
import docx
from langchain_community.embeddings import DashScopeEmbeddings
import os
from dotenv import load_dotenv
from supabase import Client


load_dotenv()


embeddings = DashScopeEmbeddings(
    model=os.getenv("DASHSCOPE_EMBEDDING_MODEL"),  # 指定你想要的版本
    dashscope_api_key=os.getenv("DASHSCOPE_API_KEY")  # 或者设置环境变量 DASHSCOPE_API_KEY
)



def sliding_window_chunking(text, window_size=512, step_size=256):
    """滑动窗口切片"""
    chunks = []
    for i in range(0, len(text), step_size):
        chunk = text[i:i + window_size]
        
        if len(chunk.strip()) > 0:
            chunks.append(chunk.strip())
    
    return chunks



def extract_words(file: UploadFile,inserted_id: int,supabase: Client,agent_id: int):
    """从Word文件中提取文本并切片"""

    try:
        # 读取Word文件
        doc = docx.Document(file.file)
        
        # 提取文本
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        # 使用滑动窗口切片
        chunks = sliding_window_chunking(text)

        # print(f"agent_id: {agent_id}")
        # print(f"inserted_id: {inserted_id}")
        # print(f"切片后的文本数量: {len(chunks)}")
        for content in chunks:
            # print(f"当前切片: {content}")
            embedding = embeddings.embed_query(content)
            supabase.table("rag_vec").insert({
                "agent_id":int(agent_id),
                "file_id": inserted_id,
                "content": content,
                "vec": embedding
            }).execute()



        return chunks
    except Exception as e:
        print(f"处理Word文件时出错: {str(e)}")
        return []
    