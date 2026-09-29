import pytest
from app.ml.forecasting import predict_demand_7d
from app.ml.adaptive import apply_adaptive_forecasting


def test_normal_demand_stable_baseline():
    features = {
        "product_id": "p-1",
        "product_name": "Tata Salt 1kg",
        "current_stock": 40.0,
        "reorder_level": 10.0,
        "target_stock": 60.0,
        "sales_1d": 3.0,
        "sales_7d": 21.0,
        "sales_14d": 42.0,
        "sales_30d": 90.0,
        "daily_avg_7d": 3.0,
        "daily_avg_30d": 3.0,
        "stock_coverage_days": 13.3,
        "sales_growth": 0.0,
    }

    result = predict_demand_7d(features)

    assert result["product_name"] == "Tata Salt 1kg"
    assert result["base_forecast"] > 0.0
    assert result["adapted_forecast"] > 0.0
    assert abs(result["base_forecast"] - result["adapted_forecast"]) < 5.0
    assert result["anomaly_detected"] is False
    assert result["requires_owner_context"] is False


def test_sudden_demand_spike_anomaly_detection():
    features = {
        "product_id": "p-2",
        "product_name": "Maggi 2-Minute Noodles",
        "current_stock": 25.0,
        "reorder_level": 10.0,
        "target_stock": 80.0,
        "sales_1d": 25.0,  # Sudden massive 1d spike vs 3d/day avg
        "sales_7d": 35.0,
        "sales_14d": 50.0,
        "sales_30d": 90.0,
        "daily_avg_7d": 5.0,
        "daily_avg_30d": 3.0,
        "stock_coverage_days": 5.0,
        "sales_growth": 0.40,
    }

    result = predict_demand_7d(features)

    assert result["anomaly_detected"] is True
    assert result["change_point_detected"] is True
    assert result["anomaly_direction"] == "SUDDEN_SPIKE"
    assert result["requires_owner_context"] is True
    assert result["adapted_forecast"] > result["base_forecast"]
    assert any("acceleration" in f["factor"] or "anomaly" in f["factor"] for f in result["factors"])


def test_sudden_demand_drop_anomaly_detection():
    features = {
        "product_id": "p-3",
        "product_name": "Britannia Good Day",
        "current_stock": 50.0,
        "reorder_level": 10.0,
        "target_stock": 60.0,
        "sales_1d": 0.0,
        "sales_7d": 2.0,
        "sales_14d": 35.0,
        "sales_30d": 90.0,
        "daily_avg_7d": 0.28,
        "daily_avg_30d": 3.0,
        "stock_coverage_days": 178.0,
        "sales_growth": -0.80,
    }

    result = predict_demand_7d(features)

    assert result["anomaly_detected"] is True
    assert result["anomaly_direction"] == "SUDDEN_DROP"
    assert result["adapted_forecast"] < result["base_forecast"]


def test_weather_heatwave_impact_on_beverages():
    features = {
        "product_id": "p-4",
        "product_name": "Coca-Cola 750ml Cold Drink",
        "current_stock": 30.0,
        "reorder_level": 5.0,
        "target_stock": 50.0,
        "sales_1d": 5.0,
        "sales_7d": 35.0,
        "sales_14d": 70.0,
        "sales_30d": 150.0,
        "daily_avg_7d": 5.0,
        "daily_avg_30d": 5.0,
        "stock_coverage_days": 6.0,
        "sales_growth": 0.0,
    }

    weather_context = {"temperature_c": 36.5, "weather_condition": "Sunny", "precipitation_mm": 0.0}

    result = predict_demand_7d(features, weather_context=weather_context)

    assert result["adapted_forecast"] > result["base_forecast"]
    assert any(f["factor"] == "weather_heatwave" for f in result["factors"])


def test_market_price_drop_impact():
    features = {
        "product_id": "p-5",
        "product_name": "Fortune Sunflower Oil 1L",
        "current_stock": 20.0,
        "reorder_level": 5.0,
        "target_stock": 40.0,
        "sales_1d": 4.0,
        "sales_7d": 28.0,
        "sales_14d": 56.0,
        "sales_30d": 120.0,
        "daily_avg_7d": 4.0,
        "daily_avg_30d": 4.0,
        "stock_coverage_days": 5.0,
        "sales_growth": 0.0,
    }

    market_context = {"price_change_pct": -0.12, "commodity_name": "Sunflower Oil"}

    result = predict_demand_7d(features, market_context=market_context)

    assert result["adapted_forecast"] > result["base_forecast"]
    assert any(f["factor"] == "market_price_drop" for f in result["factors"])


def test_hindsight_event_confirmation_and_recovery():
    features = {
        "product_id": "p-6",
        "product_name": "Amul Taaza Milk 500ml",
        "current_stock": 30.0,
        "reorder_level": 5.0,
        "target_stock": 60.0,
        "sales_1d": 20.0,
        "sales_7d": 40.0,
        "sales_14d": 70.0,
        "sales_30d": 150.0,
        "daily_avg_7d": 5.7,
        "daily_avg_30d": 5.0,
        "stock_coverage_days": 5.2,
        "sales_growth": 0.15,
    }

    # Before owner confirms event: requires_owner_context is True
    res_before = predict_demand_7d(features)
    assert res_before["requires_owner_context"] is True

    # Owner confirms festival event context in Hindsight memory
    hindsight_memories = [
        {
            "memory_type": "BUSINESS_EVENT",
            "content": "Confirmed Event Context for Amul Taaza Milk: Diwali Festival Rush (FESTIVAL). Details: Bulk sweets preparation rush",
            "confidence": 0.95
        }
    ]

    res_after = predict_demand_7d(features, hindsight_memories=hindsight_memories)

    assert res_after["requires_owner_context"] is False
    assert res_after["confidence"] > res_before["confidence"]
    assert any("hindsight_event" in f["factor"] for f in res_after["factors"])
