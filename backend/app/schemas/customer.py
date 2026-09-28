from datetime import datetime
from typing import Optional, List, Any
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, EmailStr


class CustomerCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    credit_limit: Optional[Decimal] = Decimal("5000.00")


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    credit_limit: Optional[Decimal] = None
    is_active: Optional[bool] = None


class CustomerRead(BaseModel):
    id: UUID
    shop_id: UUID
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    credit_limit: Optional[Decimal] = None
    current_balance: Optional[Decimal] = Decimal("0.00")
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CustomerHistoryRead(BaseModel):
    customer: CustomerRead
    total_spend: Decimal
    purchase_frequency: int
    outstanding_amount: Decimal
    recent_sales: List[Any] = []
    khata_transactions: List[Any] = []
    complaints: List[Any] = []
