from typing import Optional, List, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, Field


class DashboardSummaryRead(BaseModel):
    today_sales: Decimal
    today_orders: int
    today_expenses: Decimal
    today_profit: Decimal
    inventory_value: Decimal
    low_stock_count: int
    out_of_stock_count: int
    top_products: List[Dict[str, Any]] = []
    slow_movers: List[Dict[str, Any]] = []
    recent_sales: List[Dict[str, Any]] = []
    recent_purchases: List[Dict[str, Any]] = []
    pending_khata: Decimal
    open_complaints_count: int
    pending_supplier_orders_count: int
    active_recommendations_count: int


class ForecastFactor(BaseModel):
    factor: str
    impact: str
    explanation: str


class ForecastResultRead(BaseModel):
    product_id: str
    product_name: str
    base_forecast: float = 0.0
    adapted_forecast: float = 0.0
    forecast_7d: float
    daily_average: float
    stock_coverage_days: float
    stockout_risk: float
    recommended_order_quantity: float
    confidence: float
    anomaly_detected: bool = False
    change_point_detected: bool = False
    anomaly_direction: Optional[str] = None
    requires_owner_context: bool = False
    factors: List[ForecastFactor] = []


class ConfirmEventContextRequest(BaseModel):
    event_title: str = Field(..., min_length=2, max_length=255)
    event_type: str = Field("BUSINESS_EVENT", max_length=50)
    description: str = Field(..., min_length=3)
