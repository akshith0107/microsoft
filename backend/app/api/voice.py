import re
from typing import List, Dict, Any, Optional
from decimal import Decimal
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_current_shop
from app.db.session import get_async_db
from app.db.models.user import User
from app.db.models.shop import Shop
from app.db.models.product import Product
from app.db.models.voice import VoiceInteraction
from app.schemas.common import APIResponse
from app.schemas.voice import VoiceCommandRequest, VoiceCommandResponse, VoiceInteractionRead
from app.integrations.sarvam import SarvamClient
from app.integrations.hindsight import HindsightClient

router = APIRouter(prefix="/voice", tags=["Voice Interaction"])

# Helper Hindi/Hinglish number parser
HINDI_NUMBER_MAP = {
    "ek": 1, "one": 1, "1": 1,
    "do": 2, "two": 2, "2": 2,
    "teen": 3, "three": 3, "3": 3,
    "char": 4, "chaar": 4, "four": 4, "4": 4,
    "paanch": 5, "panch": 5, "five": 5, "5": 5,
    "che": 6, "chhe": 6, "six": 6, "6": 6,
    "saat": 7, "seven": 7, "7": 7,
    "aath": 8, "eight": 8, "8": 8,
    "nau": 9, "nine": 9, "9": 9,
    "das": 10, "ten": 10, "10": 10,
}


def parse_hinglish_quantities_and_products(transcript: str, products: List[Product]) -> List[Dict[str, Any]]:
    """
    Parses speech text like '2 Maggi aur 3 Parle-G' or 'do maggi, teen parle'
    and matches against PostgreSQL products.
    """
    t_lower = transcript.lower()
    matched_items = []
    seen_product_ids = set()

    # Split by common delimiters: 'aur', 'and', ',', '+'
    clauses = re.split(r'\baur\b|\band\b|,|\+', t_lower)

    for clause in clauses:
        clause = clause.strip()
        if not clause:
            continue

        # Find quantity
        quantity = 1
        words = clause.split()
        for w in words:
            if w in HINDI_NUMBER_MAP:
                quantity = HINDI_NUMBER_MAP[w]
                break
            elif w.isdigit():
                quantity = int(w)
                break

        # Match product
        best_match = None
        for p in products:
            p_name = p.name.lower()
            p_brand = (p.brand or "").lower()
            p_sku = (p.sku or "").lower()

            # Check matching keywords
            if (p_name in clause or (p_brand and p_brand in clause) or (p_sku and p_sku in clause) or
                any(token in clause for token in p_name.split() if len(token) > 3)):
                best_match = p
                break

        if best_match and str(best_match.id) not in seen_product_ids:
            seen_product_ids.add(str(best_match.id))
            matched_items.append({
                "product_id": str(best_match.id),
                "name": best_match.name,
                "quantity": quantity,
                "price": float(best_match.selling_price),
                "unit": best_match.unit,
                "current_stock": float(getattr(best_match, "current_stock", 0) or 0)
            })

    return matched_items


@router.post("/command", response_model=APIResponse[VoiceCommandResponse])
async def process_voice_command(
    cmd_in: VoiceCommandRequest,
    current_user: User = Depends(get_current_user),
    shop: Shop = Depends(get_current_shop),
    db: AsyncSession = Depends(get_async_db)
):
    sarvam = SarvamClient()

    # 1. Transcribe audio if URL provided, else use raw transcript
    if cmd_in.audio_url:
        trans_res = await sarvam.transcribe_audio(cmd_in.audio_url, language=cmd_in.language or "hi")
        transcript = trans_res.get("transcript", cmd_in.transcript or "")
    else:
        transcript = cmd_in.transcript or ""

    t_lower = transcript.lower()

    # 2. Fetch active shop products for PostgreSQL matching
    prod_res = await db.execute(
        select(Product).where(Product.shop_id == shop.id, Product.is_active == True)
    )
    products = list(prod_res.scalars().all())

    # 3. Determine Intent & Resolve Items / Context
    intent = "GENERAL_QUERY"
    response_text = f"Voice command received: '{transcript}'."
    payload_data: Dict[str, Any] = {}
    action_executed = False

    # Check for Khata / Udhaar intent
    if any(k in t_lower for k in ["udhaar", "khata", "naam pe", "daal do"]):
        intent = "KHATA_UDHAAR"
        # Extract potential customer name & amount
        numbers = [int(s) for s in re.findall(r'\b\d+\b', t_lower)]
        amount = numbers[0] if numbers else 100
        payload_data = {
            "customer_query": transcript,
            "amount": amount,
            "notes": f"Voice Udhaar Entry: {transcript}"
        }
        response_text = f"Voice Khata request detected for ₹{amount}. Ready for customer confirmation."
        action_executed = True

    # Check for Inventory query intent
    elif any(k in t_lower for k in ["stock", "kitna hai", "inventory", "available"]):
        intent = "CHECK_INVENTORY"
        response_text = f"Checking inventory stock levels for: '{transcript}'."
        action_executed = True

    # Check for Billing / POS sale intent
    else:
        matched_items = parse_hinglish_quantities_and_products(transcript, products)
        if matched_items:
            intent = "CREATE_BILL"
            subtotal = sum(item["price"] * item["quantity"] for item in matched_items)
            payload_data = {
                "items": matched_items,
                "customer_id": "walk-in",
                "payment_method": "CASH",
                "subtotal": subtotal,
                "grand_total": subtotal
            }
            item_summary = ", ".join([f"{item['quantity']}x {item['name']}" for item in matched_items])
            response_text = f"Parsed voice bill ({len(matched_items)} items): {item_summary}. Total: ₹{subtotal}."
            action_executed = True

    # 4. Log persistent supplier/operational memory to Hindsight if expressed
    if any(k in t_lower for k in ["supplier", "delivery late", "kam leta hoon", "preference"]):
        hindsight = HindsightClient()
        await hindsight.remember(
            shop_id=str(shop.id),
            memory_type="SUPPLIER_EXPERIENCE",
            content=f"Voice Memory: {transcript}"
        )

    # 5. Log Voice Interaction in PostgreSQL
    voice_log = VoiceInteraction(
        shop_id=shop.id,
        user_id=current_user.id,
        audio_url=cmd_in.audio_url,
        transcript=transcript,
        language=cmd_in.language or "hi",
        intent=intent,
        confidence=Decimal("0.95"),
        action_executed=action_executed
    )
    db.add(voice_log)
    await db.commit()

    return APIResponse(data=VoiceCommandResponse(
        transcript=transcript,
        intent=intent,
        response_text=response_text,
        action_executed=action_executed,
        data=payload_data
    ))


@router.get("/interactions", response_model=APIResponse[List[VoiceInteractionRead]])
async def list_voice_interactions(
    limit: int = Query(20, ge=1, le=100),
    shop: Shop = Depends(get_current_shop),
    db: AsyncSession = Depends(get_async_db)
):
    res = await db.execute(
        select(VoiceInteraction)
        .where(VoiceInteraction.shop_id == shop.id)
        .order_by(VoiceInteraction.created_at.desc())
        .limit(limit)
    )
    logs = list(res.scalars().all())
    return APIResponse(data=[VoiceInteractionRead.model_validate(l) for l in logs])
