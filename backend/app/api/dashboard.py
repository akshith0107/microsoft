from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_shop
from app.db.session import get_async_db
from app.db.models.shop import Shop
from app.schemas.common import APIResponse
from app.schemas.analytics import DashboardSummaryRead
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=APIResponse[DashboardSummaryRead])
async def get_dashboard(
    shop: Shop = Depends(get_current_shop),
    db: AsyncSession = Depends(get_async_db)
):
    service = AnalyticsService(db)
    summary = await service.get_dashboard_summary(shop.id)
    return APIResponse(data=DashboardSummaryRead(**summary))
