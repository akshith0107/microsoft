from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_current_shop
from app.core.exceptions import NotFoundException
from app.db.session import get_async_db
from app.db.models.user import User
from app.db.models.shop import Shop
from app.db.models.conversation import Conversation
from app.schemas.common import APIResponse
from app.schemas.conversation import ConversationRead

router = APIRouter(prefix="/conversations", tags=["Conversations"])


@router.get("", response_model=APIResponse[List[ConversationRead]])
async def list_conversations(
    shop: Shop = Depends(get_current_shop),
    db: AsyncSession = Depends(get_async_db)
):
    res = await db.execute(
        select(Conversation)
        .where(Conversation.shop_id == shop.id)
        .order_by(Conversation.last_message_at.desc())
    )
    convs = list(res.scalars().all())
    return APIResponse(data=[ConversationRead.model_validate(c) for c in convs])


@router.get("/{id}", response_model=APIResponse[ConversationRead])
async def get_conversation(
    id: UUID,
    shop: Shop = Depends(get_current_shop),
    db: AsyncSession = Depends(get_async_db)
):
    res = await db.execute(
        select(Conversation).where(Conversation.id == id, Conversation.shop_id == shop.id)
    )
    conv = res.scalar_one_or_none()
    if not conv:
        raise NotFoundException("Conversation not found")
    return APIResponse(data=ConversationRead.model_validate(conv))
