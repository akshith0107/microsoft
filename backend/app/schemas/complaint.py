from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from app.db.models.complaint import ComplaintStatus, ComplaintPriority


class ComplaintCreate(BaseModel):
    customer_id: Optional[UUID] = None
    sale_id: Optional[UUID] = None
    subject: str
    description: str
    priority: ComplaintPriority = ComplaintPriority.MEDIUM


class ComplaintUpdate(BaseModel):
    status: Optional[ComplaintStatus] = None
    priority: Optional[ComplaintPriority] = None
    assigned_to: Optional[UUID] = None
    resolution: Optional[str] = None


class ComplaintResolveRequest(BaseModel):
    resolution: str


class ComplaintRead(BaseModel):
    id: UUID
    shop_id: UUID
    customer_id: Optional[UUID] = None
    customer_name: Optional[str] = None
    sale_id: Optional[UUID] = None
    subject: str
    description: str
    status: ComplaintStatus
    priority: ComplaintPriority
    resolution: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_by: Optional[UUID] = None
    assigned_to: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
