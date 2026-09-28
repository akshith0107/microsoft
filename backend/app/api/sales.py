from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_current_shop
from app.core.exceptions import NotFoundException
from app.db.session import get_async_db
from app.db.models.user import User
from app.db.models.shop import Shop
from app.schemas.common import APIResponse
from app.schemas.sale import SaleCreate, SaleRead
from app.services.sales_service import SalesService

router = APIRouter(prefix="/sales", tags=["Sales / POS"])


@router.post("", response_model=APIResponse[SaleRead])
async def create_sale(
    sale_in: SaleCreate,
    current_user: User = Depends(get_current_user),
    shop: Shop = Depends(get_current_shop),
    db: AsyncSession = Depends(get_async_db)
):
    service = SalesService(db)
    sale = await service.create_sale(shop.id, current_user, sale_in)
    return APIResponse(data=SaleRead.model_validate(sale), message="Sale processed successfully")


@router.get("", response_model=APIResponse[List[SaleRead]])
async def list_sales(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    shop: Shop = Depends(get_current_shop),
    db: AsyncSession = Depends(get_async_db)
):
    service = SalesService(db)
    sales = await service.get_sales(shop.id, skip=skip, limit=limit)
    return APIResponse(data=[SaleRead.model_validate(s) for s in sales])


@router.get("/{id}", response_model=APIResponse[SaleRead])
async def get_sale(
    id: UUID,
    shop: Shop = Depends(get_current_shop),
    db: AsyncSession = Depends(get_async_db)
):
    service = SalesService(db)
    sale = await service.get_sale_by_id(shop.id, id)
    if not sale:
        raise NotFoundException("Sale transaction not found")
    return APIResponse(data=SaleRead.model_validate(sale))
