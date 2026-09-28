from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_current_shop, require_role
from app.core.exceptions import NotFoundException
from app.db.session import get_async_db
from app.db.models.user import User
from app.db.models.shop import Shop, ShopMember, Role
from app.schemas.common import APIResponse
from app.schemas.shop import ShopCreate, ShopUpdate, ShopRead, ShopMemberRead

router = APIRouter(prefix="/shops", tags=["Shops"])


@router.get("", response_model=APIResponse[List[ShopRead]])
async def list_shops(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    res = await db.execute(
        select(Shop)
        .join(ShopMember, ShopMember.shop_id == Shop.id)
        .where(ShopMember.user_id == current_user.id, ShopMember.is_active == True)
    )
    shops = list(res.scalars().all())
    return APIResponse(data=[ShopRead.model_validate(s) for s in shops])


@router.post("", response_model=APIResponse[ShopRead])
async def create_shop(
    shop_in: ShopCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    shop = Shop(
        name=shop_in.name,
        owner_id=current_user.id,
        phone=shop_in.phone,
        email=shop_in.email,
        address_line1=shop_in.address_line1,
        address_line2=shop_in.address_line2,
        city=shop_in.city,
        state=shop_in.state,
        pincode=shop_in.pincode,
        country=shop_in.country,
        currency=shop_in.currency,
        timezone=shop_in.timezone
    )
    db.add(shop)
    await db.flush()

    member = ShopMember(
        shop_id=shop.id,
        user_id=current_user.id,
        role=Role.OWNER,
        is_active=True
    )
    db.add(member)
    await db.commit()
    await db.refresh(shop)

    return APIResponse(data=ShopRead.model_validate(shop), message="Shop created successfully")


@router.get("/{id}", response_model=APIResponse[ShopRead])
async def get_shop_by_id(
    id: UUID,
    shop: Shop = Depends(get_current_shop)
):
    return APIResponse(data=ShopRead.model_validate(shop))
