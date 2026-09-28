from datetime import datetime
from typing import Optional, Any
from decimal import Decimal
from sqlalchemy import String, Numeric, DateTime, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, UUIDMixin

JSONType = JSONB().with_variant(JSON, "sqlite")


class WeatherObservation(Base, UUIDMixin):
    __tablename__ = "weather_observations"

    location_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    latitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(9, 6), nullable=True)
    longitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(9, 6), nullable=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    temperature_c: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    humidity: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    precipitation_mm: Mapped[Optional[Decimal]] = mapped_column(Numeric(6, 2), nullable=True)
    precipitation_probability: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    weather_condition: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    raw_data: Mapped[Optional[Any]] = mapped_column(JSONType, nullable=True)
    source: Mapped[str] = mapped_column(String(50), default="OpenWeather", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
