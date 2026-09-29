from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class SellingPredictionRequest(BaseModel):
    turn_number: int = Field(default=1, ge=1, description="Negotiation/order turn number")
    kirana_historical_trust_score: float = Field(default=0.85, ge=0.0, le=1.0, description="Store historical trust score (0-1)")
    distributor_credit_limit_allocated: float = Field(default=50000.0, ge=0.0, description="Distributor credit limit allocated")
    current_turn_offer_price: float = Field(default=100.0, gt=0.0, description="Current item offer/listing price")
    price_elasticity_demanded: float = Field(default=-1.0, description="Demand price elasticity index")
    sentiment_intensity_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Buyer/seller sentiment score")
    geographic_tier: int = Field(default=1, ge=1, le=4, description="City/region tier (1-4)")
    state_context: int = Field(default=1, ge=1, description="State/regional context code")
    commodity_type: int = Field(default=1, ge=1, description="Commodity/category classification ID")
    negotiation_posture: int = Field(default=1, ge=1, le=3, description="Negotiation strategy posture (1: Flexible, 2: Standard, 3: Firm)")

class SellingPredictionResponse(BaseModel):
    predicted_selling_price: float
    suggested_min_price: float
    suggested_max_price: float
    features_used: Dict[str, Any]
    model_status: str
