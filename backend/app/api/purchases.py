from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_current_shop
from app.db.session import get_async_db
from app.db.models.user import User
from app.db.models.shop import Shop
from app.schemas.common import APIResponse
from app.schemas.purchase import PurchaseCreate, PurchaseRead
from app.services.purchase_service import PurchaseService

router = APIRouter(prefix="/purchases", tags=["Purchases"])


@router.post("", response_model=APIResponse[PurchaseRead])
async def create_purchase(
    purchase_in: PurchaseCreate,
    current_user: User = Depends(get_current_user),
    shop: Shop = Depends(get_current_shop),
    db: AsyncSession = Depends(get_async_db)
):
    service = PurchaseService(db)
    purchase = await service.create_purchase(shop.id, current_user, purchase_in)
    return APIResponse(data=PurchaseRead.model_validate(purchase), message="Purchase recorded successfully")


@router.get("", response_model=APIResponse[List[PurchaseRead]])
async def list_purchases(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    shop: Shop = Depends(get_current_shop),
    db: AsyncSession = Depends(get_async_db)
):
    service = PurchaseService(db)
    purchases = await service.get_purchases(shop.id, skip=skip, limit=limit)
    return APIResponse(data=[PurchaseRead.model_validate(p) for p in purchases])
