from datetime import datetime
from typing import Optional, Any
import uuid
from decimal import Decimal
from sqlalchemy import String, Numeric, ForeignKey, UniqueConstraint, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, UUIDMixin

JSONType = JSONB().with_variant(JSON, "sqlite")


class MarketPriceObservation(Base, UUIDMixin):
    __tablename__ = "market_price_observations"

    commodity_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    variety: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    market_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    district: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    arrival_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    min_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    max_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    modal_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    unit: Mapped[str] = mapped_column(String(50), default="Quintal", nullable=False)
    source: Mapped[str] = mapped_column(String(50), default="Agmarknet", nullable=False)
    external_reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    raw_data: Mapped[Optional[Any]] = mapped_column(JSONType, nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class ProductMarketMapping(Base, UUIDMixin):
    __tablename__ = "product_market_mappings"
    __table_args__ = (
        UniqueConstraint("shop_id", "product_id", name="uq_product_market_mappings_shop_product"),
    )

    shop_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("shops.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    commodity_name: Mapped[str] = mapped_column(String(100), nullable=False)
    variety: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
