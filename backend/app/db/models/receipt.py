import enum
from datetime import datetime
from typing import Optional, List, Any
import uuid
from decimal import Decimal
from sqlalchemy import String, Numeric, ForeignKey, Enum, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, UUIDMixin, TimestampMixin

JSONType = JSONB().with_variant(JSON, "sqlite")


class OCRProcessingStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ReceiptScan(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "receipt_scans"

    shop_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("shops.id", ondelete="CASCADE"), nullable=False, index=True)
    uploaded_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    vendor_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    invoice_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    invoice_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    subtotal: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    tax_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    total_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    extracted_data: Mapped[Optional[Any]] = mapped_column(JSONType, nullable=True)
    processing_status: Mapped[OCRProcessingStatus] = mapped_column(Enum(OCRProcessingStatus, name="ocr_processing_status_enum"), default=OCRProcessingStatus.PENDING, nullable=False)

    items: Mapped[List["ReceiptScanItem"]] = relationship("ReceiptScanItem", back_populates="receipt_scan", cascade="all, delete-orphan")


class ReceiptScanItem(Base, UUIDMixin):
    __tablename__ = "receipt_scan_items"

    receipt_scan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("receipt_scans.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    extracted_name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 3), nullable=True)
    unit_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    total: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    confidence: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4), nullable=True)

    receipt_scan: Mapped["ReceiptScan"] = relationship("ReceiptScan", back_populates="items")
