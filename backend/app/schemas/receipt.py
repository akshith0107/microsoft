from datetime import datetime
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel
from app.db.models.receipt import OCRProcessingStatus


class ReceiptItemConfirm(BaseModel):
    product_id: Optional[UUID] = None
    extracted_name: str
    quantity: Decimal
    unit_price: Decimal


class ReceiptConfirmRequest(BaseModel):
    supplier_id: Optional[UUID] = None
    invoice_number: Optional[str] = None
    items: List[ReceiptItemConfirm]


class ReceiptScanItemRead(BaseModel):
    id: UUID
    receipt_scan_id: UUID
    product_id: Optional[UUID] = None
    extracted_name: str
    quantity: Optional[Decimal] = None
    unit_price: Optional[Decimal] = None
    total: Optional[Decimal] = None
    confidence: Optional[Decimal] = None

    class Config:
        from_attributes = True


class ReceiptScanRead(BaseModel):
    id: UUID
    shop_id: UUID
    uploaded_by: UUID
    image_url: str
    vendor_name: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[datetime] = None
    subtotal: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None
    processing_status: OCRProcessingStatus
    created_at: datetime
    items: List[ReceiptScanItemRead] = []

    class Config:
        from_attributes = True
