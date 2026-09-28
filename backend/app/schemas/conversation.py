from datetime import datetime
from typing import Optional, List, Any
from uuid import UUID
from pydantic import BaseModel
from app.db.models.conversation import MessageRole, MessageType


class ConversationMessageCreate(BaseModel):
    content: str
    message_type: MessageType = MessageType.TEXT
    extra_metadata: Optional[Any] = None


class ConversationMessageRead(BaseModel):
    id: UUID
    conversation_id: UUID
    role: MessageRole
    content: str
    message_type: MessageType
    extra_metadata: Optional[Any] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationRead(BaseModel):
    id: UUID
    shop_id: UUID
    user_id: UUID
    title: Optional[str] = None
    started_at: datetime
    last_message_at: datetime
    created_at: datetime
    messages: List[ConversationMessageRead] = []

    class Config:
        from_attributes = True


class AssistantChatRequest(BaseModel):
    message: str
    conversation_id: Optional[UUID] = None
    language: Optional[str] = "en"


class AssistantChatResponse(BaseModel):
    response: str
    conversation_id: UUID
    message_id: UUID
    intent: Optional[str] = None
    recommendation_id: Optional[UUID] = None
