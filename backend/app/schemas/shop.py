from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr
from app.db.models.shop import Role


class ShopCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    country: str = "IN"
    currency: str = "INR"
    timezone: str = "Asia/Kolkata"


class ShopUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None


class ShopRead(BaseModel):
    id: UUID
    name: str
    owner_id: UUID
    phone: Optional[str] = None
    email: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    country: str
    currency: str
    timezone: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ShopMemberCreate(BaseModel):
    user_email: EmailStr
    role: Role = Role.STAFF


class ShopMemberUpdate(BaseModel):
    role: Optional[Role] = None
    is_active: Optional[bool] = None


class ShopMemberRead(BaseModel):
    id: UUID
    shop_id: UUID
    user_id: UUID
    role: Role
    is_active: bool
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
