from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ConflictException
from app.db.models.user import User
from app.db.models.customer import Customer
from app.db.models.khata import KhataAccount, KhataTransaction, KhataTransactionType
from app.db.models.audit import AuditLog
from app.schemas.khata import KhataPaymentRequest, KhataAdjustmentRequest


class KhataService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_account(self, shop_id: UUID, customer_id: UUID) -> KhataAccount:
        res = await self.db.execute(
            select(KhataAccount).where(
                KhataAccount.shop_id == shop_id,
                KhataAccount.customer_id == customer_id
            )
        )
        account = res.scalar_one_or_none()
        if not account:
            c_res = await self.db.execute(select(Customer).where(Customer.id == customer_id, Customer.shop_id == shop_id))
            customer = c_res.scalar_one_or_none()
            if not customer:
                raise NotFoundException("Customer not found")

            account = KhataAccount(
                shop_id=shop_id,
                customer_id=customer_id,
                credit_limit=customer.credit_limit,
                current_balance=Decimal("0.00")
            )
            self.db.add(account)
            await self.db.commit()
            await self.db.refresh(account)
        return account

    async def record_payment(self, shop_id: UUID, customer_id: UUID, current_user: User, payment_in: KhataPaymentRequest) -> KhataTransaction:
        async with self.db.begin_nested():
            account = await self.get_or_create_account(shop_id, customer_id)

            account.current_balance -= payment_in.amount

            tx = KhataTransaction(
                shop_id=shop_id,
                khata_account_id=account.id,
                transaction_type=KhataTransactionType.PAYMENT,
                amount=payment_in.amount,
                reference_type=payment_in.reference_type or "PAYMENT",
                reference_id=payment_in.reference_id,
                description=payment_in.description,
                transaction_date=datetime.now(timezone.utc),
                created_by=current_user.id
            )
            self.db.add(tx)

            audit = AuditLog(
                shop_id=shop_id,
                user_id=current_user.id,
                action="KHATA_PAYMENT",
                entity_type="KhataAccount",
                entity_id=str(account.id),
                new_values={"amount": str(payment_in.amount), "new_balance": str(account.current_balance)}
            )
            self.db.add(audit)

        await self.db.commit()
        await self.db.refresh(tx)
        return tx

    async def record_adjustment(self, shop_id: UUID, customer_id: UUID, current_user: User, adj_in: KhataAdjustmentRequest) -> KhataTransaction:
        async with self.db.begin_nested():
            account = await self.get_or_create_account(shop_id, customer_id)

            if adj_in.transaction_type == KhataTransactionType.CREDIT:
                account.current_balance += adj_in.amount
            elif adj_in.transaction_type in [KhataTransactionType.PAYMENT, KhataTransactionType.ADJUSTMENT]:
                account.current_balance -= adj_in.amount

            tx = KhataTransaction(
                shop_id=shop_id,
                khata_account_id=account.id,
                transaction_type=adj_in.transaction_type,
                amount=adj_in.amount,
                reference_type="ADJUSTMENT",
                description=adj_in.description,
                transaction_date=datetime.now(timezone.utc),
                created_by=current_user.id
            )
            self.db.add(tx)

        await self.db.commit()
        await self.db.refresh(tx)
        return tx

    async def get_transactions(self, shop_id: UUID, customer_id: UUID, skip: int = 0, limit: int = 50) -> List[KhataTransaction]:
        account = await self.get_or_create_account(shop_id, customer_id)
        res = await self.db.execute(
            select(KhataTransaction)
            .where(KhataTransaction.khata_account_id == account.id)
            .order_by(KhataTransaction.transaction_date.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(res.scalars().all())
