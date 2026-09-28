from datetime import datetime
from typing import Optional
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field
from app.db.models.inventory import MovementType


class InventoryRead(BaseModel):
    id: UUID
    shop_id: UUID
    product_id: UUID
    product_name: Optional[str] = None
    product_sku: Optional[str] = None
    quantity: Decimal
    reserved_quantity: Decimal
    available_quantity: Decimal
    average_cost: Decimal
    last_purchase_price: Decimal
    last_sold_at: Optional[datetime] = None
    last_restocked_at: Optional[datetime] = None
    updated_at: datetime

    class Config:
        from_attributes = True


class InventoryAdjustmentRequest(BaseModel):
    movement_type: MovementType
    quantity: Decimal = Field(..., gt=0)
    unit_cost: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = None


class InventoryMovementRead(BaseModel):
    id: UUID
    shop_id: UUID
    product_id: UUID
    movement_type: MovementType
    quantity: Decimal
    unit_cost: Optional[Decimal] = None
    reference_type: Optional[str] = None
    reference_id: Optional[UUID] = None
    notes: Optional[str] = None
    created_by: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True
