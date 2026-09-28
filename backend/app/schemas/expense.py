from datetime import datetime
from typing import Optional
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field


class ExpenseCategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None


class ExpenseCreate(BaseModel):
    category_id: Optional[UUID] = None
    amount: Decimal = Field(..., gt=0)
    description: str
    expense_date: Optional[datetime] = None
    payment_method: str = "CASH"


class ExpenseRead(BaseModel):
    id: UUID
    shop_id: UUID
    category_id: Optional[UUID] = None
    category_name: Optional[str] = None
    amount: Decimal
    description: str
    expense_date: datetime
    payment_method: str
    created_by: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True
