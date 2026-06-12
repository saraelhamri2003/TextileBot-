from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class MessageBase(BaseModel):
    content: str

class MessageCreate(MessageBase):
    pass

class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    sender: str
    content: str
    sources: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True

class ConversationBase(BaseModel):
    title: str

class ConversationCreate(BaseModel):
    title: Optional[str] = "Nouvelle discussion"

class ConversationResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    user_id: int
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True
