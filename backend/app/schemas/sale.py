from datetime import datetime
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field
from app.db.models.sale import PaymentMethod, PaymentStatus


class SaleItemCreate(BaseModel):
    product_id: UUID
    quantity: Decimal = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)
    discount: Decimal = Field(Decimal("0.00"), ge=0)
    tax_rate: Decimal = Field(Decimal("0.00"), ge=0)


class SaleCreate(BaseModel):
    customer_id: Optional[UUID] = None
    invoice_number: Optional[str] = None
    sale_date: Optional[datetime] = None
    payment_method: PaymentMethod = PaymentMethod.CASH
    payment_status: PaymentStatus = PaymentStatus.PAID
    discount_amount: Decimal = Field(Decimal("0.00"), ge=0)
    notes: Optional[str] = None
    items: List[SaleItemCreate] = Field(..., min_items=1)


class SaleItemRead(BaseModel):
    id: UUID
    sale_id: UUID
    product_id: UUID
    product_name: Optional[str] = None
    quantity: Decimal
    unit_price: Decimal
    discount: Decimal
    tax_rate: Decimal
    total: Decimal

    class Config:
        from_attributes = True


class SaleRead(BaseModel):
    id: UUID
    shop_id: UUID
    customer_id: Optional[UUID] = None
    customer_name: Optional[str] = None
    invoice_number: str
    sale_date: datetime
    subtotal: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    payment_method: PaymentMethod
    payment_status: PaymentStatus
    notes: Optional[str] = None
    created_by: Optional[UUID] = None
    created_at: datetime
    items: List[SaleItemRead] = []

    class Config:
        from_attributes = True
