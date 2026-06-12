import json
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.database import get_db
from backend.app.core.security import get_current_user
from backend.app.models.user import User
from backend.app.models.conversation import Conversation, Message
from backend.app.schemas.conversation import ConversationResponse, ConversationCreate, MessageResponse, MessageCreate
from backend.app.services.vector_store import QdrantVectorStore
from backend.app.services.llm import LocalLLM

router = APIRouter(prefix="/chat", tags=["Chat & RAG"])
logger = logging.getLogger(__name__)

@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(
    conv_in: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conv = Conversation(
        title=conv_in.title or "Nouvelle discussion",
        user_id=current_user.id
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv

@router.get("/conversations", response_model=List[ConversationResponse])
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Conversation).filter(Conversation.user_id == current_user.id).order_by(Conversation.created_at.desc()).all()

@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Discussion non trouvée.")
    return conv

@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Discussion non trouvée.")
    db.delete(conv)
    db.commit()
    return None

@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
def send_message(
    conversation_id: int,
    msg_in: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Discussion non trouvée.")

    # Save user message
    user_msg = Message(
        conversation_id=conversation_id,
        sender="user",
        content=msg_in.content
    )
    db.add(user_msg)
    
    # Auto-rename title if it's default
    if conv.title == "Nouvelle discussion":
        conv.title = msg_in.content[:40] + ("..." if len(msg_in.content) > 40 else "")

    # Perform Vector Search
    try:
        contexts = QdrantVectorStore.search_similar(
            owner_id=current_user.id,
            query=msg_in.content,
            limit=4
        )
    except Exception as e:
        logger.exception("Vector search failed for user_id=%s", current_user.id)
        contexts = []

    # Generate Response from RAG
    bot_response_text, sources = LocalLLM.generate_response(
        query=msg_in.content,
        contexts=contexts
    )

    # Save bot message
    bot_msg = Message(
        conversation_id=conversation_id,
        sender="bot",
        content=bot_response_text,
        sources=json.dumps(sources) if sources else None
    )
    db.add(bot_msg)
    db.commit()
    db.refresh(bot_msg)
    
    return bot_msg
