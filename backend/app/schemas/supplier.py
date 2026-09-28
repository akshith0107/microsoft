from datetime import datetime
from typing import Optional
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, EmailStr


class SupplierCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    payment_terms: Optional[str] = None
    average_lead_time_days: Optional[int] = 3


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    payment_terms: Optional[str] = None
    average_lead_time_days: Optional[int] = None
    reliability_score: Optional[Decimal] = None
    is_active: Optional[bool] = None


class SupplierRead(BaseModel):
    id: UUID
    shop_id: UUID
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    payment_terms: Optional[str] = None
    average_lead_time_days: Optional[int] = None
    reliability_score: Optional[Decimal] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
