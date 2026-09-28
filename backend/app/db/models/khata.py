import enum
from datetime import datetime
from typing import Optional, List
import uuid
from decimal import Decimal
from sqlalchemy import String, Text, Numeric, ForeignKey, UniqueConstraint, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, UUIDMixin, TimestampMixin


class KhataTransactionType(str, enum.Enum):
    CREDIT = "CREDIT"
    PAYMENT = "PAYMENT"
    ADJUSTMENT = "ADJUSTMENT"


class KhataAccount(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "khata_accounts"
    __table_args__ = (
        UniqueConstraint("shop_id", "customer_id", name="uq_khata_accounts_shop_customer"),
    )

    shop_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("shops.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    credit_limit: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), default=Decimal("5000.00"), nullable=True)
    current_balance: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)

    customer: Mapped["Customer"] = relationship("Customer", back_populates="khata_account")
    transactions: Mapped[List["KhataTransaction"]] = relationship("KhataTransaction", back_populates="khata_account", cascade="all, delete-orphan")


class KhataTransaction(Base, UUIDMixin):
    __tablename__ = "khata_transactions"

    shop_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("shops.id", ondelete="CASCADE"), nullable=False, index=True)
    khata_account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("khata_accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    transaction_type: Mapped[KhataTransactionType] = mapped_column(Enum(KhataTransactionType, name="khata_transaction_type_enum"), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    reference_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    reference_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    transaction_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    khata_account: Mapped["KhataAccount"] = relationship("KhataAccount", back_populates="transactions")
