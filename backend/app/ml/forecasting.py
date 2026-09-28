from typing import Dict, Any
from app.ml.explanations import generate_interpretable_factors


def predict_demand_7d(features: Dict[str, Any]) -> Dict[str, Any]:
    daily_avg_7d = features.get("daily_avg_7d", 0.0)
    daily_avg_30d = features.get("daily_avg_30d", 0.0)
    sales_growth = features.get("sales_growth", 0.0)
    current_stock = features.get("current_stock", 0.0)
    target_stock = features.get("target_stock", 50.0)

    # Base weighted forecast: 70% recent 7d velocity + 30% 30d baseline + growth factor
    base_daily = (0.70 * daily_avg_7d) + (0.30 * daily_avg_30d)
    growth_multiplier = 1.0 + max(-0.3, min(0.5, sales_growth))
    projected_daily = max(0.5, base_daily * growth_multiplier)

    forecast_7d = round(projected_daily * 7.0, 1)
    daily_average = round(projected_daily, 2)

    stock_coverage = round(current_stock / projected_daily, 1) if projected_daily > 0 else 999.0
    stockout_risk = round(min(1.0, max(0.0, (7.0 - stock_coverage) / 7.0)), 2) if stock_coverage < 7.0 else 0.0

    recommended_order_qty = max(0.0, round(target_stock - current_stock + (projected_daily * 3.0), 1))
    confidence = 0.85 if features.get("sales_30d", 0) > 10 else 0.60

    factors = generate_interpretable_factors(features, forecast_7d, stockout_risk)

    return {
        "product_id": features.get("product_id"),
        "product_name": features.get("product_name"),
        "forecast_7d": forecast_7d,
        "daily_average": daily_average,
        "stock_coverage_days": stock_coverage,
        "stockout_risk": stockout_risk,
        "recommended_order_quantity": recommended_order_qty,
        "confidence": confidence,
        "factors": factors
    }
