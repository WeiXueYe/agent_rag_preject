from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from auth import authenticate
import os
from supabase import create_client, ClientOptions
from rag.extract_word import extract_words, sliding_window_chunking
from rag.extract_pdfs import extract_pdfs



router = APIRouter()


def get_supabase_by_token(token: str):
    url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    anon_key = os.getenv("NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY")
    options = ClientOptions(headers={"Authorization": f"Bearer {token}"})
    return create_client(url, anon_key, options=options)


@router.post("/receive_files")
async def upload_files(
    files: list[UploadFile] = File(...),
    agent_id: int = Form(...),
    current_user: dict = Depends(authenticate)
):
    
    payload = current_user["payload"]
    user_id = payload["sub"]
    supabase = get_supabase_by_token(current_user["token"])

    for file in files:
        try:
            file_extension = file.filename.split('.')[-1].lower()
            # 检查文件是否已存在
            existing_files = supabase.table("rag_files").select("id").eq("file_title", file.filename).eq("agent_id", agent_id).eq("user_id", user_id).execute()
            
            if existing_files.data and len(existing_files.data) > 0:
                raise HTTPException(
                    status_code=409,
                    detail=f"文件 '{file.filename}' 已存在，请勿重复上传"
                )
            
            # 插入新文件
            response = supabase.table("rag_files").insert({
                    "agent_id": int(agent_id),
                    "user_id": str(user_id),
                    "file_title": file.filename,
                    "file_type": file_extension
                }).execute()
            
            inserted_id = response.data[0]['id']
            print(f"操作成功，ID 为: {inserted_id}")
        except HTTPException:
            raise
        except Exception as e:
            print(f"发生错误: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"文件上传失败: {str(e)}"
            )

    try:
        print(f"agent_id: {agent_id}")
        # 处理不同类型的文件
        for file in files:
            # 提取文件扩展名
            file_extension = file.filename.split('.')[-1].lower()
            
            print(f"file_extension: {file_extension}")
            print(f"file.filename: {file.filename}")
            print(f"file.type: {type(file)}")

            # 根据文件类型进行处理
            if file_extension in ['doc', 'docx']:
                extract_words(file,inserted_id,supabase,agent_id)
                print(f"处理Word文件: {file.filename}")
                # Word文件处理逻辑
            elif file_extension == 'pdf':
                extract_pdfs(file,inserted_id,supabase,agent_id)
                print(f"处理PDF文件: {file.filename}")
                # PDF文件处理逻辑
            elif file_extension in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
                print(f"处理图片文件: {file.filename}")
                # 图片文件处理逻辑
            elif file_extension == 'txt':
                print(f"处理文本文件: {file.filename}")
                # 文本文件处理逻辑
            else:
                file_extension = 'other'
                print(f"处理其他文件: {file.filename}")
                # 其他文件处理逻辑
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "文件上传成功"
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")
    