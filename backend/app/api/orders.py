from typing import List
from uuid import UUID
from datetime import datetime, timezone
from decimal import Decimal
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_current_shop
from app.db.session import get_async_db
from app.db.models.user import User
from app.db.models.shop import Shop
from app.db.models.order import Order, OrderItem, OrderStatus
from app.schemas.common import APIResponse
from app.schemas.order import OrderCreate, OrderRead

router = APIRouter(prefix="/orders", tags=["Supplier Restock Orders"])


@router.get("", response_model=APIResponse[List[OrderRead]])
async def list_orders(
    shop: Shop = Depends(get_current_shop),
    db: AsyncSession = Depends(get_async_db)
):
    res = await db.execute(
        select(Order).where(Order.shop_id == shop.id).order_by(Order.ordered_at.desc())
    )
    orders = list(res.scalars().all())
    return APIResponse(data=[OrderRead.model_validate(o) for o in orders])


@router.post("", response_model=APIResponse[OrderRead])
async def create_order(
    ord_in: OrderCreate,
    current_user: User = Depends(get_current_user),
    shop: Shop = Depends(get_current_shop),
    db: AsyncSession = Depends(get_async_db)
):
    async with db.begin_nested():
        order = Order(
            shop_id=shop.id,
            supplier_id=ord_in.supplier_id,
            order_type=ord_in.order_type,
            status=OrderStatus.PENDING,
            expected_delivery_date=ord_in.expected_delivery_date,
            ordered_at=datetime.now(timezone.utc),
            notes=ord_in.notes,
            created_by=current_user.id
        )
        db.add(order)
        await db.flush()

        total = Decimal("0.00")
        for item in ord_in.items:
            unit_p = item.unit_price or Decimal("0.00")
            line_tot = item.quantity * unit_p
            total += line_tot

            oi = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total=line_tot
            )
            db.add(oi)

        order.total_amount = total

    await db.commit()
    await db.refresh(order)
    return APIResponse(data=OrderRead.model_validate(order), message="Restock order created successfully")
