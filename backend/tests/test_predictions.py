import pytest

@pytest.mark.asyncio
async def test_model_info(client):
    response = await client.get("/api/v1/predictions/model-info")
    assert response.status_code == 200
    data = response.json()
    assert data["model_loaded"] is True
    assert data["model_type"] == "LGBMRegressor"
    assert "features" in data
    assert len(data["features"]) == 10

@pytest.mark.asyncio
async def test_predict_selling_price(client):
    payload = {
        "turn_number": 1,
        "kirana_historical_trust_score": 0.85,
        "distributor_credit_limit_allocated": 50000.0,
        "current_turn_offer_price": 120.0,
        "price_elasticity_demanded": -1.2,
        "sentiment_intensity_score": 0.7,
        "geographic_tier": 1,
        "state_context": 1,
        "commodity_type": 1,
        "negotiation_posture": 1
    }
    response = await client.post("/api/v1/predictions/predict-selling", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "predicted_selling_price" in data
    assert data["predicted_selling_price"] > 0
    assert "suggested_min_price" in data
    assert "suggested_max_price" in data
    assert data["model_status"] == "lightgbm_negotiation_lgb_model"
