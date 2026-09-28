from datetime import datetime
from typing import Optional, List
import uuid
from decimal import Decimal
from sqlalchemy import String, Text, Numeric, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, UUIDMixin, TimestampMixin


class ExpenseCategory(Base, UUIDMixin):
    __tablename__ = "expense_categories"
    __table_args__ = (
        UniqueConstraint("shop_id", "name", name="uq_expense_categories_shop_name"),
    )

    shop_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("shops.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    expenses: Mapped[List["Expense"]] = relationship("Expense", back_populates="category")


class Expense(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "expenses"

    shop_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("shops.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("expense_categories.id", ondelete="SET NULL"), nullable=True, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    expense_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    payment_method: Mapped[str] = mapped_column(String(50), default="CASH", nullable=False)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    category: Mapped[Optional["ExpenseCategory"]] = relationship("ExpenseCategory", back_populates="expenses")
