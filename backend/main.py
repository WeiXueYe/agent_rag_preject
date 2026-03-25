from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from chat import router as chat_router
from recent import router as recent_router
from receive_file import router as receive_file_router



app = FastAPI(title="Agent-RAG-backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  #允许哪些"前端地址"访问
    allow_methods=["*"],  #允许哪些 HTTP 方法 （get/post/put/delete等）
    allow_headers=["*"],  #允许哪些请求头（如：Authorization、Content-Type等）
)

app.include_router(chat_router)
app.include_router(recent_router)  
app.include_router(receive_file_router)