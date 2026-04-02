from fastapi import UploadFile
from langchain_community.embeddings import DashScopeEmbeddings
import os
from dotenv import load_dotenv
from supabase import Client
import base64
import fitz  # PyMuPDF
from langchain_community.chat_models import ChatTongyi
from langchain_core.messages import HumanMessage
import tempfile

load_dotenv()

DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY')
if not DASHSCOPE_API_KEY:
    raise ValueError("请设置环境变量 DASHSCOPE_API_KEY")

def sliding_window_chunking(text, window_size=512, step_size=256):
    """滑动窗口切片"""
    chunks = []
    for i in range(0, len(text), step_size):
        chunk = text[i:i + window_size]
        
        if len(chunk.strip()) > 0:
            chunks.append(chunk.strip())
    
    return chunks

embeddings = DashScopeEmbeddings(
    model=os.getenv("DASHSCOPE_EMBEDDING_MODEL"),
    dashscope_api_key=os.getenv("DASHSCOPE_API_KEY")
)

def encode_pdf_to_base64(pdf_path: str) -> list:
    """
    将 PDF 的每一页转换为图片，并编码为 base64
    """
    doc = fitz.open(pdf_path)
    base64_images = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        # 为了让 LLM 看得清楚，设置较高的分辨率 DPI (例如 200)
        pix = page.get_pixmap(dpi=200)
        img_bytes = pix.tobytes("png")
        base64_str = base64.b64encode(img_bytes).decode('utf-8')
        base64_images.append(base64_str)
        
    doc.close()
    return base64_images

def let_llm_read_pdf_directly(pdf_path: str) -> str:
    """让多模态大模型直接阅读 PDF 图片"""
    
    # 1. 初始化支持视觉能力的模型 (qwen-vl-max 或 qwen-vl-plus)
    llm = ChatTongyi(
        model_name="qwen-vl-max", 
        dashscope_api_key=DASHSCOPE_API_KEY,
        temperature=0
    )
    
    # 2. 将 PDF 转为 base64 图片列表
    print("正在将 PDF 转换为图片...")
    base64_images = encode_pdf_to_base64(pdf_path)
    
    # 3. 构造多模态消息内容
    # ChatTongyi 多模态消息格式
    content = [
        "请仔细阅读这份PDF文档，提取出所有文本内容。"
    ]
    
    for img_str in base64_images:
        content.append({
            "type": "image",
            "image": f"data:image/png;base64,{img_str}"
        })
    
    # 4. 调用模型
    print("正在请求大模型直接解析 PDF 图像...")
    message = HumanMessage(content=content)
    response = llm.invoke([message])
    
    return response.content

def process_llm_result(result) -> str:
    """
    处理LLM返回的结果，提取文本内容
    """
    ans = ""
    for item in result:
        if isinstance(item, dict) and 'text' in item:
            ans += item['text']
            ans += '\n'
    return ans

def extract_pdfs(file: UploadFile, inserted_id: int, supabase: Client, agent_id: int):
    """从PDF文件中提取文本并切片"""

    try:
        # 1. 将上传的文件保存为临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(file.file.read())
            temp_file_path = temp_file.name
        
        try:
            # 2. 使用多模态大模型直接阅读PDF
            print("开始处理PDF文件...")
            result = let_llm_read_pdf_directly(temp_file_path)
            
            # 3. 处理LLM返回的结果，提取文本内容
            print("正在提取文本内容...")
            text = process_llm_result(result)
            print(f"提取的文本长度: {len(text)} 字符")
            
            # 4. 使用滑动窗口切片
            chunks = sliding_window_chunking(text)
            print(f"文本被分割成 {len(chunks)} 个块")

            # 5. 生成向量嵌入并存储到数据库
            for i, content in enumerate(chunks):
                print(f"正在处理第 {i+1}/{len(chunks)} 个文本块...")
                embedding = embeddings.embed_query(content)
                supabase.table("rag_vec").insert({
                    "agent_id": int(agent_id),
                    "file_id": inserted_id,
                    "content": content,
                    "vec": embedding
                }).execute()

            print(f"PDF文件处理完成，共处理 {len(chunks)} 个文本块")
            return chunks
            
        finally:
            # 6. 删除临时文件
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        print(f"处理PDF文件时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return []
