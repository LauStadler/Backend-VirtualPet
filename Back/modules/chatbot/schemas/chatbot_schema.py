from pydantic import BaseModel
from typing import Optional, List, Dict

class ChatMessage(BaseModel):
    role: str # 'user' o 'model'
    parts: List[str]

class ChatQueryRequest(BaseModel):
    message: str
    user_id: Optional[int] = None
    history: Optional[List[ChatMessage]] = None

class ChatQueryResponse(BaseModel):
    response: str
