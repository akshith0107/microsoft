from typing import Dict, Any, List, Optional
from datetime import datetime, timezone


def apply_adaptive_forecasting(
    base_forecast_data: Dict[str, Any],
    features: Dict[str, Any],
    weather_context: Optional[Dict[str, Any]] = None,
    market_context: Optional[Dict[str, Any]] = None,
    hindsight_memories: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Online Adaptation Layer over the Base Demand Forecast.
    Does NOT retrain the base model. Adjusts prediction using:
    1. Online EWMA / rolling short-term sales velocity ratio.
    2. Change-point / anomaly detection for sudden demand shifts.
    3. Weather observations (temperature, precipitation).
    4. Market price changes (Agmarknet commodity trends).
    5. Hindsight business context (confirmed events, local festivals, owner rules).
    """
    base_forecast = float(base_forecast_data.get("forecast_7d", 0.0))
    base_daily = float(base_forecast_data.get("daily_average", 0.0))
    product_name = base_forecast_data.get("product_name", "Product")

    # 1. Rolling Short-Term Sales Velocity Ratio
    sales_1d = float(features.get("sales_1d", 0.0))
    sales_7d = float(features.get("sales_7d", 0.0))
    sales_30d = float(features.get("sales_30d", 0.0))

    daily_avg_7d = sales_7d / 7.0
    daily_avg_30d = sales_30d / 30.0

    # Short-term exponentially weighted velocity (50% 1d, 35% 7d, 15% 30d)
    short_term_velocity = (0.50 * sales_1d) + (0.35 * daily_avg_7d) + (0.15 * daily_avg_30d)
    
    baseline_reference = max(0.2, base_daily)
    velocity_ratio = short_term_velocity / baseline_reference

    # Clamp velocity adaptation ratio to reasonable bounds [0.4, 2.5]
    clamped_velocity_ratio = max(0.4, min(2.5, velocity_ratio))

    # 2. Contextual Multipliers
    context_multiplier = 1.0
    context_factors: List[Dict[str, str]] = []

    # A. Weather Context
    if weather_context:
        temp = float(weather_context.get("temperature_c", 25.0) or 25.0)
        condition = (weather_context.get("weather_condition") or "").lower()
        precip = float(weather_context.get("precipitation_mm", 0.0) or 0.0)

        is_beverage_or_cool = any(k in product_name.lower() for k in ["coca", "coke", "thums", "pepsi", "milk", "cold", "drink", "water", "ice", "juice"])
        is_hot_drink_or_soup = any(k in product_name.lower() for k in ["tea", "chai", "coffee", "soup", "noodle", "maggi"])

        if temp >= 32.0 and is_beverage_or_cool:
            w_boost = 1.20
            context_multiplier *= w_boost
            context_factors.append({
                "factor": "weather_heatwave",
                "impact": "high",
                "explanation": f"High temperature ({temp}°C) expected to boost beverage demand by +20%."
            })
        elif temp <= 16.0 and is_hot_drink_or_soup:
            w_boost = 1.15
            context_multiplier *= w_boost
            context_factors.append({
                "factor": "weather_chilly",
                "impact": "medium",
                "explanation": f"Chilly weather ({temp}°C) boosting warm beverage & noodle demand by +15%."
            })
        
        if precip > 10.0:
            context_multiplier *= 0.90
            context_factors.append({
                "factor": "weather_rain",
                "impact": "medium",
                "explanation": f"Heavy rain ({precip}mm) estimated to reduce overall footfall by -10%."
            })

    # B. Market Price Context (Agmarknet)
    if market_context:
        price_change_pct = float(market_context.get("price_change_pct", 0.0))
        if price_change_pct <= -0.08:
            context_multiplier *= 1.15
            context_factors.append({
                "factor": "market_price_drop",
                "impact": "medium",
                "explanation": f"Wholesale market price dropped by {abs(int(price_change_pct*100))}%, driving +15% volume."
            })
        elif price_change_pct >= 0.10:
            context_multiplier *= 0.88
            context_factors.append({
                "factor": "market_price_surge",
                "impact": "medium",
                "explanation": f"Wholesale market price increased by {int(price_change_pct*100)}%, tempering consumer demand."
            })

    # C. Hindsight Business Context & Confirmed Events
    has_confirmed_hindsight_event = False
    if hindsight_memories:
        for mem in hindsight_memories:
            content = mem.get("content", "").lower()
            m_type = mem.get("memory_type", "")

            if any(k in content for k in ["festival", "diwali", "holi", "eid", "rush", "fair", "event"]):
                context_multiplier *= 1.30
                has_confirmed_hindsight_event = True
                context_factors.append({
                    "factor": "hindsight_event",
                    "impact": "critical",
                    "explanation": f"Confirmed Business Context: '{mem.get('content')}' (+30% demand adjustment)."
                })
            elif any(k in content for k in ["construction", "roadblock", "closure", "strike"]):
                context_multiplier *= 0.75
                has_confirmed_hindsight_event = True
                context_factors.append({
                    "factor": "hindsight_disruption",
                    "impact": "high",
                    "explanation": f"Confirmed Business Context: '{mem.get('content')}' (-25% demand adjustment)."
                })

    # 3. Calculate Final Adapted Forecast
    raw_adapted_daily = base_daily * clamped_velocity_ratio * context_multiplier
    adapted_daily = round(max(0.2, raw_adapted_daily), 2)
    adapted_forecast = round(adapted_daily * 7.0, 1)

    # 4. Change-Point / Anomaly Detection
    # Compare recent 1d sales vs 30d baseline average
    std_dev_approx = max(0.5, daily_avg_30d * 0.3)
    z_score = (sales_1d - daily_avg_30d) / std_dev_approx

    anomaly_detected = False
    change_point_detected = False
    anomaly_direction = None
    requires_owner_context = False

    if abs(z_score) >= 2.0 or (sales_1d >= 2.2 * max(1.0, daily_avg_30d) and sales_1d >= 4.0):
        anomaly_detected = True
        change_point_detected = True
        anomaly_direction = "SUDDEN_SPIKE" if z_score > 0 else "SUDDEN_DROP"
        
        if not has_confirmed_hindsight_event:
            requires_owner_context = True

    # 5. Explanatory Factors Assembly
    all_factors = list(base_forecast_data.get("factors", []))

    # Add velocity factor if significant
    if clamped_velocity_ratio >= 1.15:
        all_factors.insert(0, {
            "factor": "online_sales_acceleration",
            "impact": "high",
            "explanation": f"Recent sales velocity is {int((clamped_velocity_ratio - 1) * 100)}% above 30-day baseline."
        })
    elif clamped_velocity_ratio <= 0.85:
        all_factors.insert(0, {
            "factor": "online_sales_deceleration",
            "impact": "medium",
            "explanation": f"Recent sales velocity is {int((1 - clamped_velocity_ratio) * 100)}% below 30-day baseline."
        })

    # Add contextual factors
    all_factors.extend(context_factors)

    # Add Anomaly Warning Factor if required
    if anomaly_detected:
        if requires_owner_context:
            all_factors.append({
                "factor": "unexplained_anomaly_detected",
                "impact": "critical",
                "explanation": f"⚠️ Sudden {anomaly_direction.replace('_', ' ').lower()} detected ({int(sales_1d)} units in 24h vs {daily_avg_30d:.1f}/day avg). Tap to add business context."
            })
        else:
            all_factors.append({
                "factor": "explained_anomaly_detected",
                "impact": "medium",
                "explanation": f"Sudden demand shift ({anomaly_direction.replace('_', ' ').lower()}) aligned with confirmed business event."
            })

    # Adjust confidence
    base_confidence = float(base_forecast_data.get("confidence", 0.85))
    if requires_owner_context:
        final_confidence = round(max(0.60, base_confidence - 0.15), 2)
    elif has_confirmed_hindsight_event:
        final_confidence = round(min(0.98, base_confidence + 0.10), 2)
    else:
        final_confidence = base_confidence

    # Recalculate stock coverage and recommended order quantity using adapted daily rate
    current_stock = float(features.get("current_stock", 0.0))
    target_stock = float(features.get("target_stock", 50.0))

    adapted_coverage = round(current_stock / adapted_daily, 1) if adapted_daily > 0 else 999.0
    adapted_stockout_risk = round(min(1.0, max(0.0, (7.0 - adapted_coverage) / 7.0)), 2) if adapted_coverage < 7.0 else 0.0
    adapted_order_qty = max(0.0, round(target_stock - current_stock + (adapted_daily * 3.0), 1))

    return {
        "product_id": base_forecast_data.get("product_id"),
        "product_name": base_forecast_data.get("product_name"),
        "base_forecast": base_forecast,
        "adapted_forecast": adapted_forecast,
        "forecast_7d": adapted_forecast,  # Backward compatible alias
        "daily_average": adapted_daily,
        "stock_coverage_days": adapted_coverage,
        "stockout_risk": adapted_stockout_risk,
        "recommended_order_quantity": adapted_order_qty,
        "confidence": final_confidence,
        "anomaly_detected": anomaly_detected,
        "change_point_detected": change_point_detected,
        "anomaly_direction": anomaly_direction,
        "requires_owner_context": requires_owner_context,
        "factors": all_factors
    }
