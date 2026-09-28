from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query
from app.core.dependencies import get_current_shop
from app.db.models.shop import Shop
from app.schemas.common import APIResponse
from app.integrations.agmarknet import AgmarknetClient

router = APIRouter(prefix="/market", tags=["Agmarknet Market Prices"])


@router.get("/prices", response_model=APIResponse[List[Dict[str, Any]]])
async def get_market_prices(
    commodity: str = Query("Wheat"),
    state: str = Query("Delhi"),
    shop: Shop = Depends(get_current_shop)
):
    client = AgmarknetClient()
    prices = await client.fetch_commodity_prices(commodity, state)
    return APIResponse(data=prices)
