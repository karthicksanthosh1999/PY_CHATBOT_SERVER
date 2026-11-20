import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database.database import get_db
from src.schema.chat_schema import ChatRequest, ChatResponse, ConversationResponse, MessageResponse, UpdateConversationRequest
from src.services.chat_service import ChatService
from src.dependencies.auth_dependency import get_logged_user
from src.database.models import User

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/chat",
    tags=['Chat']
)

chat_service = ChatService()

@router.post("/", response_model=ChatResponse)
def chat(data: ChatRequest, db: Session = Depends(get_db), current_user: User = Depends(get_logged_user)):
    try:
        conversation_id, answer = chat_service.chat(db, user_id=current_user.id, question=data.question, conversation_id=data.conversation_id)
        return ChatResponse(
            db=db,
            conversation_id=conversation_id,
            answer=answer,
        )

    except ValueError as error:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(error)) from error

    except Exception as error:
        db.rollback()
        logger.exception("Chat generation failed")
        raise HTTPException(status_code=502, detail="Unable to generate chat response") from error

@router.get("/", response_model= list[ConversationResponse])
def get_conversations(db: Session = Depends(get_db), current_user: User = Depends(get_logged_user)):
    conversations = chat_service.get_conversations(db, user_id=current_user.id)

    return conversations

@router.get("/{conversation_id}/messages", response_model=list[MessageResponse])
def get_messages(conversation_id: int, user_id: int, db: Session = Depends(get_db)):
    try:
        return chat_service.get_messages(db, conversation_id=conversation_id, user_id=user_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

@router.patch("/{conversation_id}", response_model=ConversationResponse)
def update_conversation( conversation_id: int, data: UpdateConversationRequest, db: Session = Depends(get_db)):
    try:
        return chat_service.update_conversation(db, conversation_id, title=data.title)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

@router.delete("/{conversation_id}")
def delete_conversation(conversation_id:int, db: Session = Depends(get_db)):
    try:
        return chat_service.delete_conversation(db, conversation_id=conversation_id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error