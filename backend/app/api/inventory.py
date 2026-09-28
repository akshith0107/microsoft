from typing import List
from uuid import UUID
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_current_shop
from app.core.exceptions import NotFoundException
from app.db.session import get_async_db
from app.db.models.user import User
from app.db.models.shop import Shop
from app.db.models.product import Product
from app.db.models.inventory import Inventory, InventoryMovement, MovementType
from app.schemas.common import APIResponse
from app.schemas.inventory import InventoryRead, InventoryAdjustmentRequest, InventoryMovementRead

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get("", response_model=APIResponse[List[InventoryRead]])
async def list_inventory(
    shop: Shop = Depends(get_current_shop),
    db: AsyncSession = Depends(get_async_db)
):
    stmt = (
        select(Inventory, Product)
        .join(Product, Product.id == Inventory.product_id)
        .where(Inventory.shop_id == shop.id, Product.is_active == True)
    )
    res = await db.execute(stmt)
    records = res.all()

    out = []
    for inv, prod in records:
        r = InventoryRead(
            id=inv.id,
            shop_id=inv.shop_id,
            product_id=inv.product_id,
            product_name=prod.name,
            product_sku=prod.sku,
            quantity=inv.quantity,
            reserved_quantity=inv.reserved_quantity,
            available_quantity=inv.quantity - inv.reserved_quantity,
            average_cost=inv.average_cost,
            last_purchase_price=inv.last_purchase_price,
            last_sold_at=inv.last_sold_at,
            last_restocked_at=inv.last_restocked_at,
            updated_at=inv.updated_at
        )
        out.append(r)
    return APIResponse(data=out)


@router.post("/{product_id}/adjust", response_model=APIResponse[InventoryRead])
async def adjust_stock(
    product_id: UUID,
    adj_in: InventoryAdjustmentRequest,
    current_user: User = Depends(get_current_user),
    shop: Shop = Depends(get_current_shop),
    db: AsyncSession = Depends(get_async_db)
):
    p_res = await db.execute(select(Product).where(Product.id == product_id, Product.shop_id == shop.id))
    prod = p_res.scalar_one_or_none()
    if not prod:
        raise NotFoundException("Product not found")

    inv_res = await db.execute(select(Inventory).where(Inventory.product_id == product_id, Inventory.shop_id == shop.id))
    inv = inv_res.scalar_one_or_none()
    if not inv:
        raise NotFoundException("Inventory record not found")

    async with db.begin_nested():
        if adj_in.movement_type in [MovementType.ADJUSTMENT_IN, MovementType.PURCHASE, MovementType.TRANSFER_IN]:
            inv.quantity += adj_in.quantity
            inv.last_restocked_at = datetime.now(timezone.utc)
        else:
            inv.quantity = max(Decimal("0.000"), inv.quantity - adj_in.quantity)

        movement = InventoryMovement(
            shop_id=shop.id,
            product_id=product_id,
            movement_type=adj_in.movement_type,
            quantity=adj_in.quantity,
            unit_cost=adj_in.unit_cost or inv.average_cost,
            reference_type="MANUAL_ADJUSTMENT",
            notes=adj_in.notes or "Manual inventory adjustment",
            created_by=current_user.id
        )
        db.add(movement)

    await db.commit()
    await db.refresh(inv)

    r = InventoryRead(
        id=inv.id,
        shop_id=inv.shop_id,
        product_id=inv.product_id,
        product_name=prod.name,
        product_sku=prod.sku,
        quantity=inv.quantity,
        reserved_quantity=inv.reserved_quantity,
        available_quantity=inv.quantity - inv.reserved_quantity,
        average_cost=inv.average_cost,
        last_purchase_price=inv.last_purchase_price,
        last_sold_at=inv.last_sold_at,
        last_restocked_at=inv.last_restocked_at,
        updated_at=inv.updated_at
    )
    return APIResponse(data=r, message="Inventory adjusted successfully")
