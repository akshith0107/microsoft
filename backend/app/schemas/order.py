from datetime import datetime
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field
from app.db.models.order import OrderType, OrderStatus


class OrderItemCreate(BaseModel):
    product_id: UUID
    quantity: Decimal = Field(..., gt=0)
    unit_price: Optional[Decimal] = Field(None, ge=0)


class OrderCreate(BaseModel):
    supplier_id: Optional[UUID] = None
    order_type: OrderType = OrderType.SUPPLIER_RESTOCK
    expected_delivery_date: Optional[datetime] = None
    notes: Optional[str] = None
    items: List[OrderItemCreate] = Field(..., min_items=1)


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    expected_delivery_date: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    notes: Optional[str] = None


class OrderItemRead(BaseModel):
    id: UUID
    order_id: UUID
    product_id: UUID
    product_name: Optional[str] = None
    quantity: Decimal
    unit_price: Optional[Decimal] = None
    total: Optional[Decimal] = None

    class Config:
        from_attributes = True


class OrderRead(BaseModel):
    id: UUID
    shop_id: UUID
    supplier_id: Optional[UUID] = None
    supplier_name: Optional[str] = None
    order_type: OrderType
    status: OrderStatus
    external_reference: Optional[str] = None
    expected_delivery_date: Optional[datetime] = None
    ordered_at: datetime
    delivered_at: Optional[datetime] = None
    total_amount: Optional[Decimal] = None
    notes: Optional[str] = None
    created_by: Optional[UUID] = None
    created_at: datetime
    items: List[OrderItemRead] = []

    class Config:
        from_attributes = True
