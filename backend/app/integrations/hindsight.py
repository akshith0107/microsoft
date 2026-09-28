from typing import Optional, List, Dict, Any
import httpx
from app.core.config import settings
from app.core.logging import logger

# Global in-memory storage for MOCK mode testing & local development
_mock_memory_store: Dict[str, List[Dict[str, Any]]] = {}


class HindsightClient:
    def __init__(self, api_url: Optional[str] = None, api_key: Optional[str] = None):
        self.api_url = api_url or getattr(settings, "HINDSIGHT_BASE_URL", None) or settings.HINDSIGHT_API_URL
        self.api_key = api_key or settings.HINDSIGHT_API_KEY
        self.is_live = bool(
            self.api_key 
            and self.api_key not in ["mock_hindsight_key", "your_hindsight_api_key_here", "CHANGE_ME", ""]
        )
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        if self.is_live:
            logger.info("Hindsight Client initialized in LIVE mode", url=self.api_url)
        else:
            logger.info("Hindsight Client initialized in MOCK mode")

    async def remember(
        self,
        shop_id: str,
        memory_type: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Stores long-term experiential memory in Hindsight.
        Ignores raw sales/inventory transactional dumps.
        """
        logger.info("Hindsight Remember called", shop_id=shop_id, memory_type=memory_type, content=content, is_live=self.is_live)

        if not self.is_live:
            # Save to in-memory mock store for shop
            if shop_id not in _mock_memory_store:
                _mock_memory_store[shop_id] = []
            _mock_memory_store[shop_id].append({
                "memory_type": memory_type,
                "content": content,
                "metadata": metadata or {},
                "confidence": 0.95
            })
            return True

        # LIVE Mode HTTP POST Request
        payload = {
            "shop_id": shop_id,
            "memory_type": memory_type,
            "content": content,
            "metadata": metadata or {}
        }
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(f"{self.api_url}/memories", json=payload, headers=self.headers)
                if resp.status_code in [200, 201]:
                    logger.info("Hindsight LIVE remember successful", status_code=resp.status_code)
                    return True
                logger.error("Hindsight LIVE remember non-200 response", status_code=resp.status_code, body=resp.text)
                return False
        except Exception as e:
            logger.error("Hindsight LIVE remember request failed, continuing safely", error=str(e))
            return False

    async def recall(self, shop_id: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Recalls relevant memories for a query from Hindsight.
        """
        logger.info("Hindsight Recall called", shop_id=shop_id, query=query, is_live=self.is_live)

        if not self.is_live:
            # Retrieve from mock store matching keywords or default fallbacks
            memories = _mock_memory_store.get(shop_id, [])
            q_lower = query.lower()

            # Filter relevant memories based on query keywords
            relevant = []
            for mem in memories:
                content_lower = mem["content"].lower()
                # Check for overlapping keywords or product names
                if any(word in content_lower for word in q_lower.split() if len(word) > 3):
                    relevant.append(mem)
                elif "maggi" in q_lower and "maggi" in content_lower:
                    relevant.append(mem)

            if not relevant:
                # Provide default seed memories for demo/dev if mock store empty for query
                if "maggi" in q_lower or "stock" in q_lower or "order" in q_lower:
                    relevant = [
                        {
                            "memory_type": "OWNER_PREFERENCE",
                            "content": "Owner preference: Main Maggi ek baar mein 35 se zyada order nahi karta.",
                            "confidence": 0.95
                        },
                        {
                            "memory_type": "RECOMMENDATION_OUTCOME",
                            "content": "Previous recommendation of 50 units was modified to 30; owner preferred smaller order due to storage constraints.",
                            "confidence": 0.90
                        }
                    ]
                else:
                    relevant = memories[:limit]

            return relevant[:limit]

        # LIVE Mode HTTP GET Search Request
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(
                    f"{self.api_url}/memories/search",
                    params={"shop_id": shop_id, "query": query, "limit": limit},
                    headers=self.headers
                )
                if resp.status_code == 200:
                    data = resp.json()
                    memories = data.get("memories", [])
                    logger.info("Hindsight LIVE recall successful", count=len(memories))
                    return memories
                logger.error("Hindsight LIVE recall non-200 response", status_code=resp.status_code)
                return []
        except Exception as e:
            logger.error("Hindsight LIVE recall request failed, returning empty list safely", error=str(e))
            return []
