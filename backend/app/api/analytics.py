from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_shop
from app.core.exceptions import NotFoundException
from app.db.session import get_async_db
from app.db.models.shop import Shop
from app.schemas.common import APIResponse
from app.schemas.analytics import ForecastResultRead
from app.ml.features import extract_product_features
from app.ml.forecasting import predict_demand_7d

router = APIRouter(prefix="/analytics", tags=["ML Analytics & Demand Forecasting"])


@router.get("/forecast/{product_id}", response_model=APIResponse[ForecastResultRead])
async def get_product_forecast(
    product_id: UUID,
    shop: Shop = Depends(get_current_shop),
    db: AsyncSession = Depends(get_async_db)
):
    features = await extract_product_features(db, shop.id, product_id)
    if not features:
        raise NotFoundException("Product features could not be extracted")

    forecast = predict_demand_7d(features)
    return APIResponse(data=ForecastResultRead(**forecast))
