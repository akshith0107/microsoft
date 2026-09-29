from typing import Dict, Any, List, Optional
from app.ml.explanations import generate_interpretable_factors
from app.ml.adaptive import apply_adaptive_forecasting


def predict_demand_7d(
    features: Dict[str, Any],
    weather_context: Optional[Dict[str, Any]] = None,
    market_context: Optional[Dict[str, Any]] = None,
    hindsight_memories: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Predicts 7-day demand using a stable base model combined with an online adaptive layer.
    1. Base Model: Weighted moving average (7d + 30d baseline + growth trend).
    2. Adaptive Layer: Dynamically adjusts for recent sales acceleration, weather, market prices, and Hindsight events.
    """
    daily_avg_7d = float(features.get("daily_avg_7d", 0.0))
    daily_avg_30d = float(features.get("daily_avg_30d", 0.0))
    sales_growth = float(features.get("sales_growth", 0.0))
    current_stock = float(features.get("current_stock", 0.0))
    target_stock = float(features.get("target_stock", 50.0))

    # Base weighted forecast: 70% recent 7d velocity + 30% 30d baseline + growth factor
    base_daily = (0.70 * daily_avg_7d) + (0.30 * daily_avg_30d)
    growth_multiplier = 1.0 + max(-0.3, min(0.5, sales_growth))
    projected_daily = max(0.2, base_daily * growth_multiplier)

    base_forecast_7d = round(projected_daily * 7.0, 1)
    base_daily_avg = round(projected_daily, 2)

    base_stock_coverage = round(current_stock / projected_daily, 1) if projected_daily > 0 else 999.0
    base_stockout_risk = round(min(1.0, max(0.0, (7.0 - base_stock_coverage) / 7.0)), 2) if base_stock_coverage < 7.0 else 0.0

    base_recommended_order_qty = max(0.0, round(target_stock - current_stock + (projected_daily * 3.0), 1))
    base_confidence = 0.85 if features.get("sales_30d", 0) > 10 else 0.60

    base_factors = generate_interpretable_factors(features, base_forecast_7d, base_stockout_risk)

    base_data = {
        "product_id": features.get("product_id"),
        "product_name": features.get("product_name"),
        "forecast_7d": base_forecast_7d,
        "daily_average": base_daily_avg,
        "stock_coverage_days": base_stock_coverage,
        "stockout_risk": base_stockout_risk,
        "recommended_order_quantity": base_recommended_order_qty,
        "confidence": base_confidence,
        "factors": base_factors
    }

    # Pass base model predictions through the online adaptive layer
    adapted_result = apply_adaptive_forecasting(
        base_forecast_data=base_data,
        features=features,
        weather_context=weather_context,
        market_context=market_context,
        hindsight_memories=hindsight_memories
    )

    return adapted_result
