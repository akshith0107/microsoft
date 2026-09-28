from typing import List
from uuid import UUID
from decimal import Decimal
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_shop
from app.core.exceptions import NotFoundException
from app.db.session import get_async_db
from app.db.models.shop import Shop
from app.db.models.customer import Customer
from app.db.models.khata import KhataAccount
from app.db.models.sale import Sale
from app.schemas.common import APIResponse
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerRead, CustomerHistoryRead

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("", response_model=APIResponse[List[CustomerRead]])
async def list_customers(
    shop: Shop = Depends(get_current_shop),
    db: AsyncSession = Depends(get_async_db)
):
    res = await db.execute(
        select(Customer).where(Customer.shop_id == shop.id, Customer.is_active == True).order_by(Customer.name.asc())
    )
    customers = list(res.scalars().all())

    out = []
    for c in customers:
        khata_res = await db.execute(
            select(KhataAccount).where(KhataAccount.customer_id == c.id, KhataAccount.shop_id == shop.id)
        )
        khata = khata_res.scalar_one_or_none()
        balance = khata.current_balance if khata else Decimal("0.00")

        r = CustomerRead.model_validate(c)
        r.current_balance = balance
        out.append(r)

    return APIResponse(data=out)


@router.post("", response_model=APIResponse[CustomerRead])
async def create_customer(
    cust_in: CustomerCreate,
    shop: Shop = Depends(get_current_shop),
    db: AsyncSession = Depends(get_async_db)
):
    cust = Customer(
        shop_id=shop.id,
        name=cust_in.name,
        phone=cust_in.phone,
        email=cust_in.email,
        address=cust_in.address,
        notes=cust_in.notes,
        credit_limit=cust_in.credit_limit
    )
    db.add(cust)
    await db.flush()

    khata = KhataAccount(
        shop_id=shop.id,
        customer_id=cust.id,
        credit_limit=cust_in.credit_limit,
        current_balance=Decimal("0.00")
    )
    db.add(khata)

    await db.commit()
    await db.refresh(cust)

    r = CustomerRead.model_validate(cust)
    r.current_balance = Decimal("0.00")
    return APIResponse(data=r, message="Customer created successfully")


@router.get("/{id}/history", response_model=APIResponse[CustomerHistoryRead])
async def get_customer_history(
    id: UUID,
    shop: Shop = Depends(get_current_shop),
    db: AsyncSession = Depends(get_async_db)
):
    c_res = await db.execute(select(Customer).where(Customer.id == id, Customer.shop_id == shop.id))
    cust = c_res.scalar_one_or_none()
    if not cust:
        raise NotFoundException("Customer not found")

    spend_res = await db.execute(
        select(
            func.coalesce(func.sum(Sale.total_amount), Decimal("0.00")),
            func.count(Sale.id)
        ).where(Sale.customer_id == id, Sale.shop_id == shop.id)
    )
    total_spend, frequency = spend_res.one()

    khata_res = await db.execute(
        select(KhataAccount).where(KhataAccount.customer_id == id, KhataAccount.shop_id == shop.id)
    )
    khata = khata_res.scalar_one_or_none()
    balance = khata.current_balance if khata else Decimal("0.00")

    c_read = CustomerRead.model_validate(cust)
    c_read.current_balance = balance

    return APIResponse(data=CustomerHistoryRead(
        customer=c_read,
        total_spend=total_spend,
        purchase_frequency=frequency,
        outstanding_amount=balance,
        recent_sales=[],
        khata_transactions=[],
        complaints=[]
    ))
