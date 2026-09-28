import enum
from datetime import datetime
from typing import Optional, List
import uuid
from sqlalchemy import String, Text, ForeignKey, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, UUIDMixin, TimestampMixin


class RecommendationType(str, enum.Enum):
    STOCK = "STOCK"
    PURCHASE = "PURCHASE"
    SALES = "SALES"
    PRICING = "PRICING"
    CUSTOMER = "CUSTOMER"
    SUPPLIER = "SUPPLIER"
    EXPENSE = "EXPENSE"
    GROWTH = "GROWTH"
    MARKET = "MARKET"
    WEATHER = "WEATHER"
    GENERAL = "GENERAL"


class RecommendationStatus(str, enum.Enum):
    NEW = "NEW"
    VIEWED = "VIEWED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"
    EXPIRED = "EXPIRED"


class DecisionType(str, enum.Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    MODIFIED = "MODIFIED"
    IGNORED = "IGNORED"


class OutcomeType(str, enum.Enum):
    SUCCESS = "SUCCESS"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
    FAILURE = "FAILURE"
    UNKNOWN = "UNKNOWN"


class Recommendation(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "recommendations"

    shop_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("shops.id", ondelete="CASCADE"), nullable=False, index=True)
    type: Mapped[RecommendationType] = mapped_column(Enum(RecommendationType, name="recommendation_type_enum"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    reasoning: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(String(20), default="MEDIUM", nullable=False)
    related_product_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    related_supplier_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("suppliers.id", ondelete="SET NULL"), nullable=True)
    related_customer_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[RecommendationStatus] = mapped_column(Enum(RecommendationStatus, name="recommendation_status_enum"), default=RecommendationStatus.NEW, nullable=False, index=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    outcomes: Mapped[List["RecommendationOutcome"]] = relationship("RecommendationOutcome", back_populates="recommendation", cascade="all, delete-orphan")


class RecommendationOutcome(Base, UUIDMixin):
    __tablename__ = "recommendation_outcomes"

    recommendation_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("recommendations.id", ondelete="CASCADE"), nullable=False, index=True)
    shop_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("shops.id", ondelete="CASCADE"), nullable=False, index=True)
    decision: Mapped[DecisionType] = mapped_column(Enum(DecisionType, name="decision_type_enum"), nullable=False)
    decision_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    outcome: Mapped[OutcomeType] = mapped_column(Enum(OutcomeType, name="outcome_type_enum"), default=OutcomeType.UNKNOWN, nullable=False)
    outcome_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    measured_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    recommendation: Mapped["Recommendation"] = relationship("Recommendation", back_populates="outcomes")
