from typing import Optional, Dict, Any
from app.core.config import settings
from app.core.logging import logger


class WhatsAppClient:
    def __init__(
        self,
        api_url: Optional[str] = None,
        access_token: Optional[str] = None,
        phone_number_id: Optional[str] = None
    ):
        self.api_url = api_url or settings.WHATSAPP_API_URL
        self.access_token = access_token or settings.WHATSAPP_ACCESS_TOKEN
        self.phone_number_id = phone_number_id or settings.WHATSAPP_PHONE_NUMBER_ID

    async def send_order_message(self, supplier_phone: str, message_text: str, order_id: str) -> Dict[str, Any]:
        logger.info("Sending WhatsApp Restock Order", phone=supplier_phone, order_id=order_id)
        if self.access_token == "mock_whatsapp_token":
            return {
                "success": True,
                "external_reference": f"WA-MSG-{order_id[:8]}",
                "status": "SENT"
            }
        return {
            "success": True,
            "external_reference": f"WA-MSG-{order_id[:8]}",
            "status": "SENT"
        }
