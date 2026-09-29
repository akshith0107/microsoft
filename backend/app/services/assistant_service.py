from datetime import datetime, timezone
from typing import Optional, Dict, Any
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User
from app.db.models.shop import Shop
from app.db.models.conversation import Conversation, ConversationMessage, MessageRole, MessageType
from app.db.models.recommendation import Recommendation, RecommendationType, RecommendationStatus
from app.db.models.product import Product
from app.db.models.inventory import Inventory
from app.integrations.hindsight import HindsightClient
from app.integrations.gemini import GeminiClient
from app.ml.features import extract_product_features
from app.ml.forecasting import predict_demand_7d
from app.schemas.conversation import AssistantChatRequest, AssistantChatResponse


def is_persistent_memory_candidate(text: str) -> bool:
    """
    Quality filter: Checks whether user statement contains persistent owner preferences,
    business decisions, constraints, or operational rules worth storing in Hindsight.
    Ignores transient banter like 'hello', 'show dashboard', 'today sales'.
    """
    t_lower = text.lower()
    
    # Generic banter to ignore
    banter_phrases = ["hello", "hi", "hey", "okay", "ok", "show dashboard", "what are today's sales", "good morning"]
    if any(t_lower == phrase or t_lower.startswith(phrase + " ") for phrase in banter_phrases):
        return False

    # Persistent indicators
    persistent_keywords = [
        "nahi karta", "nahi karta hu", "preference", "limit", "don't order", "do not order",
        "max ", "maximum", "storage", "space", "supplier", "deliver", "always", "never",
        "season", "demand", "zyada", "kam order", "rules"
    ]
    return any(kw in t_lower for kw in persistent_keywords)


class AssistantService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.hindsight = HindsightClient()
        self.gemini = GeminiClient()

    async def process_chat(self, shop: Shop, current_user: User, chat_in: AssistantChatRequest) -> AssistantChatResponse:
        # 1. Resolve or create conversation
        if chat_in.conversation_id:
            res = await self.db.execute(
                select(Conversation).where(
                    Conversation.id == chat_in.conversation_id,
                    Conversation.shop_id == shop.id
                )
            )
            conversation = res.scalar_one_or_none()
        else:
            conversation = None

        if not conversation:
            conversation = Conversation(
                shop_id=shop.id,
                user_id=current_user.id,
                title=f"Chat {datetime.now().strftime('%b %d, %H:%M')}",
                started_at=datetime.now(timezone.utc),
                last_message_at=datetime.now(timezone.utc)
            )
            self.db.add(conversation)
            await self.db.flush()

        # 2. Save User Message
        user_msg = ConversationMessage(
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content=chat_in.message,
            message_type=MessageType.TEXT
        )
        self.db.add(user_msg)

        # 3. Fetch PostgreSQL DB Context (Facts)
        product_res = await self.db.execute(
            select(Product).where(Product.shop_id == shop.id, Product.is_active == True)
        )
        products = list(product_res.scalars().all())

        matched_product = None
        user_text = chat_in.message.lower()
        for p in products:
            name_match = bool(p.name and p.name.lower() in user_text)
            sku_match = bool(p.sku and p.sku.lower() in user_text)
            brand_match = bool(p.brand and p.brand.lower() in user_text)
            if name_match or sku_match or brand_match:
                matched_product = p
                break

        db_facts = {
            "shop_name": shop.name,
            "city": shop.city,
            "currency": shop.currency,
            "active_products_count": len(products)
        }

        ml_outputs = None
        if matched_product:
            features = await extract_product_features(self.db, shop.id, matched_product.id)
            if features:
                ml_outputs = predict_demand_7d(features)
                db_facts["matched_product"] = {
                    "name": matched_product.name,
                    "stock": features.get("current_stock"),
                    "reorder_level": features.get("reorder_level")
                }

        # 4. Recall Relevant Hindsight Memories
        memories = await self.hindsight.recall(str(shop.id), chat_in.message, limit=5)

        # 5. Call Gemini Reasoning over Facts + ML + Memories
        response_text = await self.gemini.generate_response(
            prompt=chat_in.message,
            context={"db_facts": db_facts},
            memories=memories,
            ml_outputs=ml_outputs
        )

        # 6. Save Assistant Response Message
        assistant_msg = ConversationMessage(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=response_text,
            message_type=MessageType.TEXT
        )
        self.db.add(assistant_msg)
        conversation.last_message_at = datetime.now(timezone.utc)

        # 7. Quality Check & Remember Persistent Owner Statements in Hindsight
        if is_persistent_memory_candidate(chat_in.message):
            await self.hindsight.remember(
                shop_id=str(shop.id),
                memory_type="OWNER_PREFERENCE",
                content=f"Owner statement: {chat_in.message}"
            )

        # 8. Create recommendation record if reorder/stock action item generated
        recommendation_id = None
        msg_lower = chat_in.message.lower()
        if "order" in msg_lower or "restock" in msg_lower or "kitna" in msg_lower:
            rec = Recommendation(
                shop_id=shop.id,
                type=RecommendationType.STOCK,
                title=f"Restock Recommendation for {matched_product.name if matched_product else 'Inventory'}",
                recommendation=response_text,
                reasoning="Generated based on PostgreSQL stock, 7-day ML forecast, and Hindsight owner memory.",
                priority="HIGH",
                related_product_id=matched_product.id if matched_product else None,
                status=RecommendationStatus.NEW
            )
            self.db.add(rec)
            await self.db.flush()
            recommendation_id = rec.id

        await self.db.commit()

        return AssistantChatResponse(
            response=response_text,
            conversation_id=conversation.id,
            message_id=assistant_msg.id,
            intent="ASSISTANT_QUERY",
            recommendation_id=recommendation_id
        )
