from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from auth import authenticate
from memory.recent_memory import RecentMemory
import os
import shutil
router = APIRouter()


@router.post("/receive_files")
async def upload_files(
    files: list[UploadFile] = File(...),
    current_user: dict = Depends(authenticate)
):
    try:
        # do nothing for now
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "文件上传成功"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")
    