from datetime import datetime
from typing import Optional
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field
from app.db.models.khata import KhataTransactionType


class KhataPaymentRequest(BaseModel):
    amount: Decimal = Field(..., gt=0)
    description: str = Field("Payment received", min_length=1)
    reference_type: Optional[str] = "PAYMENT"
    reference_id: Optional[UUID] = None


class KhataAdjustmentRequest(BaseModel):
    amount: Decimal = Field(..., gt=0)
    transaction_type: KhataTransactionType = KhataTransactionType.ADJUSTMENT
    description: str = Field(..., min_length=1)


class KhataTransactionRead(BaseModel):
    id: UUID
    shop_id: UUID
    khata_account_id: UUID
    transaction_type: KhataTransactionType
    amount: Decimal
    reference_type: Optional[str] = None
    reference_id: Optional[UUID] = None
    description: str
    transaction_date: datetime
    created_by: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True


class KhataAccountRead(BaseModel):
    id: UUID
    shop_id: UUID
    customer_id: UUID
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    credit_limit: Optional[Decimal] = None
    current_balance: Decimal
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
