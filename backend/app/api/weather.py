from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, Query
from app.core.dependencies import get_current_shop
from app.db.models.shop import Shop
from app.schemas.common import APIResponse
from app.integrations.weather import WeatherClient

router = APIRouter(prefix="/weather", tags=["Weather Integration"])


@router.get("", response_model=APIResponse[Dict[str, Any]])
async def get_weather(
    location: Optional[str] = Query("Delhi"),
    shop: Shop = Depends(get_current_shop)
):
    client = WeatherClient()
    loc = location or shop.city or "Delhi"
    data = await client.get_current_weather(loc)
    return APIResponse(data=data)
