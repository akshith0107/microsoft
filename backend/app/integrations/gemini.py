from typing import Optional, Dict, Any, List
import httpx
from app.core.config import settings
from app.core.logging import logger


class GeminiClient:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL
        self.is_live = bool(
            self.api_key 
            and self.api_key not in ["mock_gemini_key", "your_gemini_api_key_here", "CHANGE_ME", ""]
        )

        if self.is_live:
            logger.info("Gemini Client initialized in LIVE mode", model=self.model)
        else:
            logger.info("Gemini Client initialized in MOCK mode")

    async def generate_response(
        self,
        prompt: str,
        context: Dict[str, Any],
        memories: List[Dict[str, Any]],
        ml_outputs: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generates a personalized response combining:
        1. PostgreSQL Facts
        2. ML Forecasts
        3. Hindsight Experiential Memories
        """
        logger.info("Calling Gemini Client generate_response", prompt=prompt, is_live=self.is_live)

        db_facts = context.get("db_facts", {})
        shop_name = db_facts.get("shop_name", "Shop")

        # Format 3 distinct context sections
        facts_text = f"Shop Name: {shop_name}\n" + "\n".join([f"- {k}: {v}" for k, v in db_facts.items()])
        ml_text = "\n".join([f"- {k}: {v}" for k, v in (ml_outputs or {}).items()]) if ml_outputs else "No active ML forecast for this query."
        memories_text = "\n".join([f"- [{mem.get('memory_type', 'MEMORY')}] {mem.get('content')}" for mem in memories]) if memories else "No prior shop memory recorded for this item."

        if not self.is_live:
            # MOCK Mode: Intelligent response synthesis using facts, ML, and memories
            p_lower = prompt.lower()
            if "maggi" in p_lower or "order" in p_lower or "stock" in p_lower:
                matched_p = db_facts.get("matched_product", {})
                current_stock = matched_p.get("stock", 12)
                p_name = matched_p.get("name", "Maggi 2-Min Masala Noodle 70g")

                # Check if any recalled memory specifies an owner preference limit
                has_owner_limit = any("35" in mem.get("content", "") or "limit" in mem.get("content", "").lower() for mem in memories)

                if has_owner_limit:
                    return (
                        f"{p_name} ka current stock {current_stock} packets hai. ML forecast ke hisaab se 7-day demand high hai, "
                        f"lekin aapki Hindsight memory preference ke mutabiq aap ek baar mein 35 se zyada order nahi karte. "
                        f"Isliye 30 packets order karna safest and optimal decision rahega."
                    )
                else:
                    return (
                        f"{p_name} ka current stock {current_stock} packets hai. Recent sales velocity ko dekhte hue "
                        f"30-35 packets restock karne ki salah di jaati hai."
                    )
            elif "profit" in p_lower or "sale" in p_lower or "khata" in p_lower:
                return (
                    f"Aaj {shop_name} ki live status: Total active products count {db_facts.get('active_products_count', 0)}. "
                    f"Khata balance tracking and POS transactions are operating normally."
                )
            else:
                return (
                    f"Namaste! {shop_name} ka operational context load ho gaya hai. "
                    f"PostgreSQL facts, ML demand predictions, aur Hindsight memory synched hain. "
                    f"Aap inventory ya ordering ke baare mein pooch sakte hain."
                )

        # LIVE Mode: Call Gemini REST API
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
            
            system_instruction = (
                "You are DukaanPulse AI Assistant for an Indian Kirana store owner. "
                "Communicate in natural, respectful Hinglish or English. "
                "CRITICAL RULE: DO NOT INVENT or hallucinate quantitative facts or numbers. "
                "All quantitative metrics (stock, sales, prices, forecast numbers) MUST come strictly from CURRENT BUSINESS FACTS (PostgreSQL) or ML DEMAND FORECAST. "
                "Use RELEVANT EXPERIENTIAL SHOP MEMORY for owner preferences, past ordering decisions, supplier patterns, and business constraints."
            )

            full_prompt = (
                f"SYSTEM INSTRUCTION:\n{system_instruction}\n\n"
                f"--- 1. CURRENT BUSINESS FACTS (PostgreSQL) ---\n{facts_text}\n\n"
                f"--- 2. ML DEMAND FORECAST & PREDICTIONS ---\n{ml_text}\n\n"
                f"--- 3. RELEVANT EXPERIENTIAL SHOP MEMORY (Hindsight) ---\n{memories_text}\n\n"
                f"--- USER QUERY ---\n{prompt}"
            )

            payload = {
                "contents": [{"parts": [{"text": full_prompt}]}]
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts and "text" in parts[0]:
                            logger.info("Gemini LIVE response generated successfully")
                            return parts[0]["text"]
                logger.error("Gemini LIVE API non-200 response", status_code=resp.status_code, text=resp.text)
                return "Context retrieved from database. Gemini service is experiencing high load."

        except Exception as e:
            logger.error("Gemini LIVE API request failed, returning safe fallback", error=str(e))
            return "Apologies, AI reasoning service is currently operating in fallback mode. Please check stock levels in Inventory."
