from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_shop
from app.core.exceptions import ConflictException, NotFoundException
from app.db.session import get_async_db
from app.db.models.shop import Shop
from app.db.models.product import Product
from app.db.models.inventory import Inventory
from app.schemas.common import APIResponse
from app.schemas.product import ProductCreate, ProductUpdate, ProductRead

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=APIResponse[List[ProductRead]])
async def list_products(
    category_id: Optional[UUID] = Query(None),
    is_active: Optional[bool] = Query(True),
    shop: Shop = Depends(get_current_shop),
    db: AsyncSession = Depends(get_async_db)
):
    stmt = select(Product).where(Product.shop_id == shop.id)
    if is_active is not None:
        stmt = stmt.where(Product.is_active == is_active)
    if category_id:
        stmt = stmt.where(Product.category_id == category_id)

    stmt = stmt.order_by(Product.name.asc())
    res = await db.execute(stmt)
    products = list(res.scalars().all())

    out_list = []
    for p in products:
        inv_res = await db.execute(select(Inventory).where(Inventory.product_id == p.id, Inventory.shop_id == shop.id))
        inv = inv_res.scalar_one_or_none()
        stock = inv.quantity if inv else Decimal("0.000")

        read_item = ProductRead.model_validate(p)
        read_item.current_stock = stock
        out_list.append(read_item)

    return APIResponse(data=out_list)


@router.post("", response_model=APIResponse[ProductRead])
async def create_product(
    prod_in: ProductCreate,
    shop: Shop = Depends(get_current_shop),
    db: AsyncSession = Depends(get_async_db)
):
    # Check SKU
    res_sku = await db.execute(
        select(Product).where(Product.shop_id == shop.id, Product.sku == prod_in.sku)
    )
    if res_sku.scalar_one_or_none():
        raise ConflictException(f"Product SKU '{prod_in.sku}' already exists in this shop")

    # Check Barcode
    if prod_in.barcode:
        res_bc = await db.execute(
            select(Product).where(Product.shop_id == shop.id, Product.barcode == prod_in.barcode)
        )
        if res_bc.scalar_one_or_none():
            raise ConflictException(f"Barcode '{prod_in.barcode}' is already assigned to another product")

    prod = Product(
        shop_id=shop.id,
        category_id=prod_in.category_id,
        sku=prod_in.sku,
        barcode=prod_in.barcode,
        name=prod_in.name,
        brand=prod_in.brand,
        description=prod_in.description,
        unit=prod_in.unit,
        purchase_price=prod_in.purchase_price,
        selling_price=prod_in.selling_price,
        tax_rate=prod_in.tax_rate,
        reorder_level=prod_in.reorder_level,
        target_stock=prod_in.target_stock,
        is_active=True
    )
    db.add(prod)
    await db.flush()

    inv = Inventory(
        shop_id=shop.id,
        product_id=prod.id,
        quantity=prod_in.initial_stock or Decimal("0.000"),
        average_cost=prod_in.purchase_price,
        last_purchase_price=prod_in.purchase_price
    )
    db.add(inv)
    await db.commit()
    await db.refresh(prod)

    read_item = ProductRead.model_validate(prod)
    read_item.current_stock = inv.quantity
    return APIResponse(data=read_item, message="Product created successfully")


@router.get("/{id}", response_model=APIResponse[ProductRead])
async def get_product(
    id: UUID,
    shop: Shop = Depends(get_current_shop),
    db: AsyncSession = Depends(get_async_db)
):
    res = await db.execute(select(Product).where(Product.id == id, Product.shop_id == shop.id))
    prod = res.scalar_one_or_none()
    if not prod:
        raise NotFoundException("Product not found")

    inv_res = await db.execute(select(Inventory).where(Inventory.product_id == prod.id, Inventory.shop_id == shop.id))
    inv = inv_res.scalar_one_or_none()

    read_item = ProductRead.model_validate(prod)
    read_item.current_stock = inv.quantity if inv else Decimal("0.000")
    return APIResponse(data=read_item)


@router.delete("/{id}", response_model=APIResponse[bool])
async def delete_product(
    id: UUID,
    shop: Shop = Depends(get_current_shop),
    db: AsyncSession = Depends(get_async_db)
):
    res = await db.execute(select(Product).where(Product.id == id, Product.shop_id == shop.id))
    prod = res.scalar_one_or_none()
    if not prod:
        raise NotFoundException("Product not found")

    # Soft delete
    prod.is_active = False
    await db.commit()
    return APIResponse(data=True, message="Product deactivated successfully")
