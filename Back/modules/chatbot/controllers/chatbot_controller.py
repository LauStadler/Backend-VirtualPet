from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from shared.dependencies.database import get_db
from modules.chatbot.schemas.chatbot_schema import ChatQueryRequest, ChatQueryResponse
from modules.chatbot.services.chatbot_service import ChatbotService

router = APIRouter(tags=["chatbot"])

@router.post("/query", response_model=ChatQueryResponse)
async def chat_query(request: ChatQueryRequest, db: Session = Depends(get_db)):
    service = ChatbotService(db)
    response_text = await service.generate_response(request.message, request.user_id, request.history)
    return ChatQueryResponse(response=response_text)
