from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query
from app.core.dependencies import get_current_shop
from app.db.models.shop import Shop
from app.schemas.common import APIResponse
from app.integrations.hindsight import HindsightClient

router = APIRouter(prefix="/memory", tags=["Hindsight Long-Term AI Memory"])


@router.get("/recall", response_model=APIResponse[List[Dict[str, Any]]])
async def recall_memories(
    query: str = Query(..., min_length=1),
    limit: int = Query(5, ge=1, le=20),
    shop: Shop = Depends(get_current_shop)
):
    hindsight = HindsightClient()
    memories = await hindsight.recall(str(shop.id), query=query, limit=limit)
    return APIResponse(data=memories)
