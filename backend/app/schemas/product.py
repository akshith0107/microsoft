from datetime import datetime
from typing import Optional
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field
from app.db.models.product import Unit


class ProductCreate(BaseModel):
    category_id: Optional[UUID] = None
    sku: str
    barcode: Optional[str] = None
    name: str
    brand: Optional[str] = None
    description: Optional[str] = None
    unit: Unit = Unit.piece
    purchase_price: Decimal = Field(..., ge=0)
    selling_price: Decimal = Field(..., ge=0)
    tax_rate: Decimal = Field(Decimal("0.00"), ge=0)
    reorder_level: Decimal = Field(Decimal("10.000"), ge=0)
    target_stock: Decimal = Field(Decimal("50.000"), ge=0)
    initial_stock: Optional[Decimal] = Field(Decimal("0.000"), ge=0)


class ProductUpdate(BaseModel):
    category_id: Optional[UUID] = None
    sku: Optional[str] = None
    barcode: Optional[str] = None
    name: Optional[str] = None
    brand: Optional[str] = None
    description: Optional[str] = None
    unit: Optional[Unit] = None
    purchase_price: Optional[Decimal] = Field(None, ge=0)
    selling_price: Optional[Decimal] = Field(None, ge=0)
    tax_rate: Optional[Decimal] = Field(None, ge=0)
    reorder_level: Optional[Decimal] = Field(None, ge=0)
    target_stock: Optional[Decimal] = Field(None, ge=0)
    is_active: Optional[bool] = None


class ProductRead(BaseModel):
    id: UUID
    shop_id: UUID
    category_id: Optional[UUID] = None
    sku: str
    barcode: Optional[str] = None
    name: str
    brand: Optional[str] = None
    description: Optional[str] = None
    unit: Unit
    purchase_price: Decimal
    selling_price: Decimal
    tax_rate: Decimal
    reorder_level: Decimal
    target_stock: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime
    current_stock: Optional[Decimal] = Decimal("0.000")

    class Config:
        from_attributes = True
