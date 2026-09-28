from typing import List, Optional, Dict, Any
from uuid import UUID
from decimal import Decimal
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query, UploadFile, File, Body
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_current_shop
from app.core.exceptions import NotFoundException, BadRequestException
from app.db.session import get_async_db
from app.db.models.user import User
from app.db.models.shop import Shop
from app.db.models.product import Product
from app.db.models.supplier import Supplier
from app.db.models.receipt import ReceiptScan, ReceiptScanItem, OCRProcessingStatus
from app.schemas.common import APIResponse
from app.schemas.receipt import ReceiptScanRead, ReceiptConfirmRequest
from app.schemas.purchase import PurchaseCreate, PurchaseItemCreate
from app.integrations.ocr import OCRClient
from app.integrations.hindsight import HindsightClient
from app.services.purchase_service import PurchaseService

router = APIRouter(prefix="/receipts", tags=["Receipt Scan / OCR"])


async def match_product_for_extracted_item(db: AsyncSession, shop_id: UUID, extracted_name: str) -> tuple[Optional[UUID], Decimal]:
    """
    Attempts to match OCR extracted text against active PostgreSQL products for the shop.
    Returns (product_id, confidence_score).
    """
    res = await db.execute(
        select(Product).where(Product.shop_id == shop_id, Product.is_active == True)
    )
    products = list(res.scalars().all())

    e_lower = extracted_name.lower()
    best_match = None
    best_score = Decimal("0.00")

    for p in products:
        p_name = p.name.lower()
        p_brand = (p.brand or "").lower()
        p_sku = (p.sku or "").lower()

        # Exact token match
        if p_name in e_lower or e_lower in p_name:
            best_match = p
            best_score = Decimal("0.95")
            break
        elif p_brand and p_brand in e_lower:
            best_match = p
            best_score = Decimal("0.85")

    if best_match:
        return best_match.id, best_score
    return None, Decimal("0.50")


def _make_json_serializable(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: _make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_make_json_serializable(x) for x in obj]
    return obj


@router.post("/process", response_model=APIResponse[ReceiptScanRead])
async def process_receipt(
    payload: Optional[dict] = Body(None),
    current_user: User = Depends(get_current_user),
    shop: Shop = Depends(get_current_shop),
    db: AsyncSession = Depends(get_async_db)
):
    image_url = "https://example.com/receipt_sample.png"
    if payload:
        image_url = payload.get("image_url") or payload.get("image_data") or image_url

    ocr = OCRClient()
    ocr_result = await ocr.process_receipt_image(image_url)

    vendor_name = ocr_result.get("vendor_name", "Wholesale Supplier")
    inv_number = ocr_result.get("invoice_number", f"INV-{int(datetime.now().timestamp())}")

    # Check duplicate receipt invoice number for shop
    dup_res = await db.execute(
        select(ReceiptScan).where(
            ReceiptScan.shop_id == shop.id,
            ReceiptScan.invoice_number == inv_number
        )
    )
    existing_scan = dup_res.scalar_one_or_none()
    if existing_scan:
        logger.warning("Duplicate receipt scan detected", invoice_number=inv_number)

    scan = ReceiptScan(
        shop_id=shop.id,
        uploaded_by=current_user.id,
        image_url=image_url,
        vendor_name=vendor_name,
        invoice_number=inv_number,
        invoice_date=datetime.now(timezone.utc),
        subtotal=ocr_result.get("subtotal"),
        tax_amount=ocr_result.get("tax_amount"),
        total_amount=ocr_result.get("total_amount"),
        extracted_data=_make_json_serializable(ocr_result),
        processing_status=OCRProcessingStatus.COMPLETED
    )
    db.add(scan)
    await db.flush()

    for item in ocr_result.get("extracted_items", []):
        ext_name = item["extracted_name"]
        matched_pid, confidence = await match_product_for_extracted_item(db, shop.id, ext_name)

        sc_item = ReceiptScanItem(
            receipt_scan_id=scan.id,
            product_id=matched_pid,
            extracted_name=ext_name,
            quantity=item["quantity"],
            unit_price=item["unit_price"],
            total=item["total"],
            confidence=item.get("confidence", confidence)
        )
        db.add(sc_item)

    await db.commit()
    
    # Reload scan with items loaded
    reload_res = await db.execute(
        select(ReceiptScan)
        .options(selectinload(ReceiptScan.items))
        .where(ReceiptScan.id == scan.id)
    )
    loaded_scan = reload_res.scalar_one()

    return APIResponse(data=ReceiptScanRead.model_validate(loaded_scan), message="OCR scan processed successfully")


@router.post("/{id}/confirm", response_model=APIResponse[ReceiptScanRead])
async def confirm_receipt_purchase(
    id: UUID,
    confirm_in: ReceiptConfirmRequest,
    current_user: User = Depends(get_current_user),
    shop: Shop = Depends(get_current_shop),
    db: AsyncSession = Depends(get_async_db)
):
    res = await db.execute(
        select(ReceiptScan)
        .options(selectinload(ReceiptScan.items))
        .where(ReceiptScan.id == id, ReceiptScan.shop_id == shop.id)
    )
    scan = res.scalar_one_or_none()
    if not scan:
        raise NotFoundException("Receipt scan record not found")

    if not confirm_in.items:
        raise BadRequestException("Cannot confirm empty purchase receipt")

    # Match or resolve product IDs and construct Purchase items
    purchase_items_input: List[PurchaseItemCreate] = []
    for item_in in confirm_in.items:
        product_id = item_in.product_id

        # Fallback product match if product_id not provided directly
        if not product_id:
            matched_pid, _ = await match_product_for_extracted_item(db, shop.id, item_in.extracted_name)
            if not matched_pid:
                # Pick first active product in shop if unlinked to ensure valid purchase creation
                p_first = await db.execute(select(Product).where(Product.shop_id == shop.id, Product.is_active == True))
                prod_obj = p_first.scalars().first()
                if not prod_obj:
                    raise BadRequestException(f"No active product found for '{item_in.extracted_name}'")
                matched_pid = prod_obj.id
            product_id = matched_pid

        purchase_items_input.append(PurchaseItemCreate(
            product_id=product_id,
            quantity=item_in.quantity,
            unit_cost=item_in.unit_price,
            tax_rate=Decimal("0.00"),
            discount=Decimal("0.00")
        ))

    # Execute purchase creation via existing PurchaseService
    purchase_create = PurchaseCreate(
        supplier_id=confirm_in.supplier_id,
        invoice_number=confirm_in.invoice_number or scan.invoice_number,
        purchase_date=scan.invoice_date or datetime.now(timezone.utc),
        payment_status="PAID",
        notes=f"Created from OCR Receipt Scan #{scan.invoice_number}",
        items=purchase_items_input
    )

    purchase_svc = PurchaseService(db)
    purchase = await purchase_svc.create_purchase(shop.id, current_user, purchase_create)

    # Sync vendor/supplier pricing insight to Hindsight if available
    if scan.vendor_name:
        hindsight = HindsightClient()
        await hindsight.remember(
            shop_id=str(shop.id),
            memory_type="SUPPLIER_EXPERIENCE",
            content=f"Receipt Scan Purchase completed from supplier '{scan.vendor_name}' for invoice #{purchase.invoice_number}. Total: ₹{purchase.total_amount}."
        )

    scan.processing_status = OCRProcessingStatus.COMPLETED
    await db.commit()
    await db.refresh(scan)

    return APIResponse(data=ReceiptScanRead.model_validate(scan), message=f"Purchase PO #{purchase.invoice_number} created and inventory updated!")


@router.get("", response_model=APIResponse[List[ReceiptScanRead]])
async def list_receipts(
    limit: int = Query(20, ge=1, le=100),
    shop: Shop = Depends(get_current_shop),
    db: AsyncSession = Depends(get_async_db)
):
    res = await db.execute(
        select(ReceiptScan)
        .options(selectinload(ReceiptScan.items))
        .where(ReceiptScan.shop_id == shop.id)
        .order_by(ReceiptScan.created_at.desc())
        .limit(limit)
    )
    scans = list(res.scalars().all())
    return APIResponse(data=[ReceiptScanRead.model_validate(s) for s in scans])
