import enum
from typing import Optional
import uuid
from decimal import Decimal
from sqlalchemy import String, Text, Boolean, Numeric, ForeignKey, UniqueConstraint, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, UUIDMixin, TimestampMixin


class Unit(str, enum.Enum):
    piece = "piece"
    kg = "kg"
    g = "g"
    litre = "litre"
    ml = "ml"
    packet = "packet"
    box = "box"
    bottle = "bottle"
    dozen = "dozen"
    pouch = "pouch"


class Product(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("shop_id", "sku", name="uq_products_shop_sku"),
        UniqueConstraint("shop_id", "barcode", name="uq_products_shop_barcode"),
    )

    shop_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("shops.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    sku: Mapped[str] = mapped_column(String(100), nullable=False)
    barcode: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    brand: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    unit: Mapped[Unit] = mapped_column(Enum(Unit, name="product_unit_enum"), default=Unit.piece, nullable=False)
    
    purchase_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    selling_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"), nullable=False)
    tax_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.00"), nullable=False)
    reorder_level: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=Decimal("10.000"), nullable=False)
    target_stock: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=Decimal("50.000"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    category: Mapped[Optional["Category"]] = relationship("Category", back_populates="products")
    inventory: Mapped[Optional["Inventory"]] = relationship("Inventory", back_populates="product", uselist=False, cascade="all, delete-orphan")
