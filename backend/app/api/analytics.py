from uuid import UUID
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_current_shop
from app.core.exceptions import NotFoundException
from app.db.session import get_async_db
from app.db.models.user import User
from app.db.models.shop import Shop
from app.db.models.weather import WeatherObservation
from app.db.models.market import MarketPriceObservation, ProductMarketMapping
from app.schemas.common import APIResponse
from app.schemas.analytics import ForecastResultRead, ConfirmEventContextRequest
from app.ml.features import extract_product_features
from app.ml.forecasting import predict_demand_7d
from app.integrations.hindsight import HindsightClient

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

    # Fetch recent Weather context
    w_res = await db.execute(select(WeatherObservation).order_by(WeatherObservation.observed_at.desc()).limit(1))
    weather_obs = w_res.scalar_one_or_none()
    weather_context = None
    if weather_obs:
        weather_context = {
            "temperature_c": float(weather_obs.temperature_c) if weather_obs.temperature_c else 25.0,
            "weather_condition": weather_obs.weather_condition,
            "precipitation_mm": float(weather_obs.precipitation_mm) if weather_obs.precipitation_mm else 0.0
        }

    # Fetch recent Market Price context
    m_map_res = await db.execute(
        select(ProductMarketMapping).where(ProductMarketMapping.shop_id == shop.id, ProductMarketMapping.product_id == product_id)
    )
    p_map = m_map_res.scalar_one_or_none()
    market_context = None
    if p_map:
        m_obs_res = await db.execute(
            select(MarketPriceObservation)
            .where(MarketPriceObservation.commodity_name == p_map.commodity_name)
            .order_by(MarketPriceObservation.arrival_date.desc())
            .limit(1)
        )
        m_obs = m_obs_res.scalar_one_or_none()
        if m_obs and m_obs.modal_price:
            market_context = {
                "modal_price": float(m_obs.modal_price),
                "commodity_name": m_obs.commodity_name,
                "price_change_pct": 0.0  # Stable baseline or price delta
            }

    # Recall Hindsight memories for shop & product
    hindsight = HindsightClient()
    hindsight_memories = await hindsight.recall(str(shop.id), query=features.get("product_name", "product"))

    forecast = predict_demand_7d(
        features=features,
        weather_context=weather_context,
        market_context=market_context,
        hindsight_memories=hindsight_memories
    )

    return APIResponse(data=ForecastResultRead(**forecast))


@router.post("/forecast/{product_id}/context", response_model=APIResponse[ForecastResultRead])
async def confirm_forecast_event_context(
    product_id: UUID,
    event_in: ConfirmEventContextRequest,
    current_user: User = Depends(get_current_user),
    shop: Shop = Depends(get_current_shop),
    db: AsyncSession = Depends(get_async_db)
):
    features = await extract_product_features(db, shop.id, product_id)
    if not features:
        raise NotFoundException("Product features could not be extracted")

    # Store confirmed business event context in Hindsight memory (no raw transactional dumps)
    hindsight = HindsightClient()
    memory_content = f"Confirmed Event Context for {features.get('product_name')}: {event_in.event_title} ({event_in.event_type}). Details: {event_in.description}"
    
    await hindsight.remember(
        shop_id=str(shop.id),
        memory_type=event_in.event_type,
        content=memory_content,
        metadata={
            "product_id": str(product_id),
            "confirmed_by_user_id": str(current_user.id),
            "event_title": event_in.event_title
        }
    )

    # Re-run forecast with newly confirmed Hindsight context
    hindsight_memories = await hindsight.recall(str(shop.id), query=features.get("product_name", "product"))

    forecast = predict_demand_7d(
        features=features,
        hindsight_memories=hindsight_memories
    )

    return APIResponse(
        data=ForecastResultRead(**forecast),
        message=f"Business event context '{event_in.event_title}' recorded in Hindsight and applied to demand forecast."
    )
