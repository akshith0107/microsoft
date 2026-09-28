from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_current_shop
from app.db.session import get_async_db
from app.db.models.user import User
from app.db.models.shop import Shop
from app.schemas.common import APIResponse
from app.schemas.conversation import AssistantChatRequest, AssistantChatResponse
from app.services.assistant_service import AssistantService

router = APIRouter(prefix="/assistant", tags=["AI Assistant"])


@router.post("/chat", response_model=APIResponse[AssistantChatResponse])
async def assistant_chat(
    chat_in: AssistantChatRequest,
    current_user: User = Depends(get_current_user),
    shop: Shop = Depends(get_current_shop),
    db: AsyncSession = Depends(get_async_db)
):
    service = AssistantService(db)
    resp = await service.process_chat(shop, current_user, chat_in)
    return APIResponse(data=resp)
