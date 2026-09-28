from typing import Dict, Any, List
from decimal import Decimal
from app.core.logging import logger


class OCRClient:
    async def process_receipt_image(self, image_url: str) -> Dict[str, Any]:
        logger.info("Processing Receipt OCR", image_url=image_url)
        return {
            "vendor_name": "Gupta Wholesale Traders",
            "invoice_number": f"GWT-{int(Decimal('1000'))}",
            "subtotal": Decimal("1450.00"),
            "tax_amount": Decimal("72.50"),
            "total_amount": Decimal("1522.50"),
            "extracted_items": [
                {
                    "extracted_name": "Maggi 2-Minute Noodles 70g",
                    "quantity": Decimal("40.000"),
                    "unit_price": Decimal("12.00"),
                    "total": Decimal("480.00"),
                    "confidence": Decimal("0.96")
                },
                {
                    "extracted_name": "Parle-G 80g",
                    "quantity": Decimal("50.000"),
                    "unit_price": Decimal("9.00"),
                    "total": Decimal("450.00"),
                    "confidence": Decimal("0.94")
                },
                {
                    "extracted_name": "Tata Salt 1kg",
                    "quantity": Decimal("20.000"),
                    "unit_price": Decimal("26.00"),
                    "total": Decimal("520.00"),
                    "confidence": Decimal("0.98")
                }
            ]
        }
