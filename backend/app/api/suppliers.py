from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_shop
from app.core.exceptions import NotFoundException
from app.db.session import get_async_db
from app.db.models.shop import Shop
from app.db.models.supplier import Supplier
from app.schemas.common import APIResponse
from app.schemas.supplier import SupplierCreate, SupplierUpdate, SupplierRead

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])


@router.get("", response_model=APIResponse[List[SupplierRead]])
async def list_suppliers(
    shop: Shop = Depends(get_current_shop),
    db: AsyncSession = Depends(get_async_db)
):
    res = await db.execute(
        select(Supplier).where(Supplier.shop_id == shop.id, Supplier.is_active == True).order_by(Supplier.name.asc())
    )
    suppliers = list(res.scalars().all())
    return APIResponse(data=[SupplierRead.model_validate(s) for s in suppliers])


@router.post("", response_model=APIResponse[SupplierRead])
async def create_supplier(
    sup_in: SupplierCreate,
    shop: Shop = Depends(get_current_shop),
    db: AsyncSession = Depends(get_async_db)
):
    sup = Supplier(
        shop_id=shop.id,
        name=sup_in.name,
        phone=sup_in.phone,
        email=sup_in.email,
        address=sup_in.address,
        notes=sup_in.notes,
        payment_terms=sup_in.payment_terms,
        average_lead_time_days=sup_in.average_lead_time_days
    )
    db.add(sup)
    await db.commit()
    await db.refresh(sup)
    return APIResponse(data=SupplierRead.model_validate(sup), message="Supplier created successfully")
