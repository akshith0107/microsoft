from datetime import datetime
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field
from app.db.models.purchase import PaymentStatus


class PurchaseItemCreate(BaseModel):
    product_id: UUID
    quantity: Decimal = Field(..., gt=0)
    unit_cost: Decimal = Field(..., ge=0)
    tax_rate: Decimal = Field(Decimal("0.00"), ge=0)
    discount: Decimal = Field(Decimal("0.00"), ge=0)


class PurchaseCreate(BaseModel):
    supplier_id: Optional[UUID] = None
    invoice_number: Optional[str] = None
    purchase_date: Optional[datetime] = None
    payment_status: PaymentStatus = PaymentStatus.PAID
    notes: Optional[str] = None
    items: List[PurchaseItemCreate] = Field(..., min_items=1)


class PurchaseItemRead(BaseModel):
    id: UUID
    purchase_id: UUID
    product_id: UUID
    product_name: Optional[str] = None
    quantity: Decimal
    unit_cost: Decimal
    tax_rate: Decimal
    discount: Decimal
    total: Decimal

    class Config:
        from_attributes = True


class PurchaseRead(BaseModel):
    id: UUID
    shop_id: UUID
    supplier_id: Optional[UUID] = None
    supplier_name: Optional[str] = None
    invoice_number: Optional[str] = None
    purchase_date: datetime
    subtotal: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    total_amount: Decimal
    payment_status: PaymentStatus
    notes: Optional[str] = None
    created_by: Optional[UUID] = None
    created_at: datetime
    items: List[PurchaseItemRead] = []

    class Config:
        from_attributes = True
