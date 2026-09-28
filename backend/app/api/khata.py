from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_current_shop
from app.db.session import get_async_db
from app.db.models.user import User
from app.db.models.shop import Shop
from app.db.models.khata import KhataAccount
from app.db.models.customer import Customer
from app.schemas.common import APIResponse
from app.schemas.khata import KhataAccountRead, KhataTransactionRead, KhataPaymentRequest, KhataAdjustmentRequest
from app.services.khata_service import KhataService

router = APIRouter(prefix="/khata", tags=["Khata / Udhaar"])


@router.get("", response_model=APIResponse[List[KhataAccountRead]])
async def list_khata_accounts(
    shop: Shop = Depends(get_current_shop),
    db: AsyncSession = Depends(get_async_db)
):
    stmt = (
        select(KhataAccount, Customer)
        .join(Customer, Customer.id == KhataAccount.customer_id)
        .where(KhataAccount.shop_id == shop.id)
        .order_by(KhataAccount.current_balance.desc())
    )
    res = await db.execute(stmt)
    records = res.all()

    out = []
    for acc, cust in records:
        r = KhataAccountRead(
            id=acc.id,
            shop_id=acc.shop_id,
            customer_id=acc.customer_id,
            customer_name=cust.name,
            customer_phone=cust.phone,
            credit_limit=acc.credit_limit,
            current_balance=acc.current_balance,
            created_at=acc.created_at,
            updated_at=acc.updated_at
        )
        out.append(r)
    return APIResponse(data=out)


@router.post("/{customer_id}/payment", response_model=APIResponse[KhataTransactionRead])
async def record_khata_payment(
    customer_id: UUID,
    payment_in: KhataPaymentRequest,
    current_user: User = Depends(get_current_user),
    shop: Shop = Depends(get_current_shop),
    db: AsyncSession = Depends(get_async_db)
):
    service = KhataService(db)
    tx = await service.record_payment(shop.id, customer_id, current_user, payment_in)
    return APIResponse(data=KhataTransactionRead.model_validate(tx), message="Khata payment recorded successfully")


@router.get("/{customer_id}/transactions", response_model=APIResponse[List[KhataTransactionRead]])
async def list_customer_khata_transactions(
    customer_id: UUID,
    shop: Shop = Depends(get_current_shop),
    db: AsyncSession = Depends(get_async_db)
):
    service = KhataService(db)
    txs = await service.get_transactions(shop.id, customer_id)
    return APIResponse(data=[KhataTransactionRead.model_validate(t) for t in txs])
