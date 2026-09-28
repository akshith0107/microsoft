from datetime import datetime
from typing import Optional, Any
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel


class VoiceCommandRequest(BaseModel):
    audio_url: Optional[str] = None
    transcript: str
    language: Optional[str] = "hi"


class VoiceInteractionRead(BaseModel):
    id: UUID
    shop_id: UUID
    user_id: UUID
    audio_url: Optional[str] = None
    transcript: Optional[str] = None
    language: Optional[str] = None
    intent: Optional[str] = None
    confidence: Optional[Decimal] = None
    action_executed: bool
    created_at: datetime

    class Config:
        from_attributes = True


class VoiceCommandResponse(BaseModel):
    transcript: str
    intent: str
    response_text: str
    action_executed: bool
    data: Optional[Any] = None
