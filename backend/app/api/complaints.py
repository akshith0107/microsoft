from typing import List
from uuid import UUID
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_current_shop
from app.core.exceptions import NotFoundException
from app.db.session import get_async_db
from app.db.models.user import User
from app.db.models.shop import Shop
from app.db.models.complaint import Complaint, ComplaintStatus
from app.schemas.common import APIResponse
from app.schemas.complaint import ComplaintCreate, ComplaintUpdate, ComplaintResolveRequest, ComplaintRead

router = APIRouter(prefix="/complaints", tags=["Complaints"])


@router.get("", response_model=APIResponse[List[ComplaintRead]])
async def list_complaints(
    shop: Shop = Depends(get_current_shop),
    db: AsyncSession = Depends(get_async_db)
):
    res = await db.execute(
        select(Complaint).where(Complaint.shop_id == shop.id).order_by(Complaint.created_at.desc())
    )
    complaints = list(res.scalars().all())
    return APIResponse(data=[ComplaintRead.model_validate(c) for c in complaints])


@router.post("", response_model=APIResponse[ComplaintRead])
async def create_complaint(
    comp_in: ComplaintCreate,
    current_user: User = Depends(get_current_user),
    shop: Shop = Depends(get_current_shop),
    db: AsyncSession = Depends(get_async_db)
):
    comp = Complaint(
        shop_id=shop.id,
        customer_id=comp_in.customer_id,
        sale_id=comp_in.sale_id,
        subject=comp_in.subject,
        description=comp_in.description,
        priority=comp_in.priority,
        status=ComplaintStatus.OPEN,
        created_by=current_user.id
    )
    db.add(comp)
    await db.commit()
    await db.refresh(comp)
    return APIResponse(data=ComplaintRead.model_validate(comp), message="Complaint logged successfully")


@router.post("/{id}/resolve", response_model=APIResponse[ComplaintRead])
async def resolve_complaint(
    id: UUID,
    res_in: ComplaintResolveRequest,
    shop: Shop = Depends(get_current_shop),
    db: AsyncSession = Depends(get_async_db)
):
    res = await db.execute(select(Complaint).where(Complaint.id == id, Complaint.shop_id == shop.id))
    comp = res.scalar_one_or_none()
    if not comp:
        raise NotFoundException("Complaint not found")

    comp.status = ComplaintStatus.RESOLVED
    comp.resolution = res_in.resolution
    comp.resolved_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(comp)
    return APIResponse(data=ComplaintRead.model_validate(comp), message="Complaint marked as resolved")
