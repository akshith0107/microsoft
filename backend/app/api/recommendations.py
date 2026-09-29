from typing import List
from uuid import UUID
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_current_shop
from app.core.exceptions import NotFoundException
from app.db.session import get_async_db
from app.db.models.user import User
from app.db.models.shop import Shop
from app.db.models.recommendation import Recommendation, RecommendationOutcome, RecommendationStatus
from app.schemas.common import APIResponse
from app.schemas.recommendation import RecommendationRead, RecommendationOutcomeCreate, RecommendationOutcomeRead
from app.integrations.hindsight import HindsightClient

router = APIRouter(prefix="/recommendations", tags=["AI Recommendations"])


@router.get("", response_model=APIResponse[List[RecommendationRead]])
async def list_recommendations(
    shop: Shop = Depends(get_current_shop),
    db: AsyncSession = Depends(get_async_db)
):
    res = await db.execute(
        select(Recommendation)
        .options(selectinload(Recommendation.outcomes))
        .where(Recommendation.shop_id == shop.id)
        .order_by(Recommendation.generated_at.desc())
    )
    recs = list(res.scalars().all())
    return APIResponse(data=[RecommendationRead.model_validate(r) for r in recs])


@router.post("/{id}/decision", response_model=APIResponse[RecommendationOutcomeRead])
async def record_recommendation_decision(
    id: UUID,
    outcome_in: RecommendationOutcomeCreate,
    current_user: User = Depends(get_current_user),
    shop: Shop = Depends(get_current_shop),
    db: AsyncSession = Depends(get_async_db)
):
    res = await db.execute(
        select(Recommendation).where(Recommendation.id == id, Recommendation.shop_id == shop.id)
    )
    rec = res.scalar_one_or_none()
    if not rec:
        raise NotFoundException("Recommendation not found")

    rec.status = RecommendationStatus.ACCEPTED if outcome_in.decision.value == "ACCEPTED" else RecommendationStatus.REJECTED

    outcome = RecommendationOutcome(
        recommendation_id=rec.id,
        shop_id=shop.id,
        decision=outcome_in.decision,
        decision_notes=outcome_in.decision_notes,
        outcome=outcome_in.outcome,
        outcome_notes=outcome_in.outcome_notes,
        measured_at=datetime.now(timezone.utc),
        created_by=current_user.id
    )
    db.add(outcome)
    await db.commit()
    await db.refresh(outcome)

    # Store recommendation outcome and owner reasoning in Hindsight
    hindsight = HindsightClient()
    memory_content = (
        f"Recommendation Outcome for '{rec.title}': Decision={outcome_in.decision.value}. "
        f"Owner Reasoning: {outcome_in.decision_notes or 'No notes provided'}. "
        f"Outcome: {outcome_in.outcome or 'None'}"
    )
    await hindsight.remember(
        shop_id=str(shop.id),
        memory_type="RECOMMENDATION_OUTCOME",
        content=memory_content
    )

    return APIResponse(data=RecommendationOutcomeRead.model_validate(outcome), message="Recommendation outcome recorded and synced to Hindsight memory")
