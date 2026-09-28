from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_shop
from app.core.exceptions import ConflictException, NotFoundException
from app.db.session import get_async_db
from app.db.models.shop import Shop
from app.db.models.category import Category
from app.schemas.common import APIResponse
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryRead

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=APIResponse[List[CategoryRead]])
async def list_categories(
    shop: Shop = Depends(get_current_shop),
    db: AsyncSession = Depends(get_async_db)
):
    res = await db.execute(select(Category).where(Category.shop_id == shop.id).order_by(Category.name.asc()))
    categories = list(res.scalars().all())
    return APIResponse(data=[CategoryRead.model_validate(c) for c in categories])


@router.post("", response_model=APIResponse[CategoryRead])
async def create_category(
    cat_in: CategoryCreate,
    shop: Shop = Depends(get_current_shop),
    db: AsyncSession = Depends(get_async_db)
):
    res = await db.execute(
        select(Category).where(
            Category.shop_id == shop.id,
            Category.name == cat_in.name
        )
    )
    if res.scalar_one_or_none():
        raise ConflictException(f"Category '{cat_in.name}' already exists in this shop")

    cat = Category(
        shop_id=shop.id,
        name=cat_in.name,
        description=cat_in.description
    )
    db.add(cat)
    await db.commit()
    await db.refresh(cat)
    return APIResponse(data=CategoryRead.model_validate(cat), message="Category created")
