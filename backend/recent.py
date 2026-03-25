from pydantic import BaseModel
from fastapi import APIRouter, Depends
from memory.recent_memory import RecentMemory
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from auth import authenticate

router = APIRouter()

class ChatRequest(BaseModel):
    prompt: str
    agent_id: int


@router.post("/recent")
async def get_recent(chat_request: ChatRequest ,current_user: dict = Depends(authenticate)):

    payload = current_user["payload"]
    user_id = payload["sub"]
    agent_id = chat_request.agent_id

    recent_memory = RecentMemory(
        user_id=user_id,
        agent_id=agent_id
    )

    return recent_memory.get_list_recent(50)