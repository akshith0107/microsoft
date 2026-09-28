from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel
from app.db.models.recommendation import RecommendationType, RecommendationStatus, DecisionType, OutcomeType


class RecommendationOutcomeCreate(BaseModel):
    decision: DecisionType
    decision_notes: Optional[str] = None
    outcome: Optional[OutcomeType] = OutcomeType.UNKNOWN
    outcome_notes: Optional[str] = None


class RecommendationOutcomeRead(BaseModel):
    id: UUID
    recommendation_id: UUID
    shop_id: UUID
    decision: DecisionType
    decision_notes: Optional[str] = None
    outcome: OutcomeType
    outcome_notes: Optional[str] = None
    measured_at: Optional[datetime] = None
    created_by: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RecommendationRead(BaseModel):
    id: UUID
    shop_id: UUID
    type: RecommendationType
    title: str
    recommendation: str
    reasoning: str
    priority: str
    related_product_id: Optional[UUID] = None
    related_supplier_id: Optional[UUID] = None
    related_customer_id: Optional[UUID] = None
    status: RecommendationStatus
    generated_at: datetime
    expires_at: Optional[datetime] = None
    created_at: datetime
    outcomes: List[RecommendationOutcomeRead] = []

    class Config:
        from_attributes = True
