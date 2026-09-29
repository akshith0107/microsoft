from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.prediction import SellingPredictionRequest, SellingPredictionResponse
from app.services.prediction_service import prediction_service

router = APIRouter(prefix="/predictions", tags=["ML Predictions"])

@router.post("/predict-selling", response_model=SellingPredictionResponse)
async def predict_selling_price(request: SellingPredictionRequest):
    """
    Predict optimal selling price and negotiation range for Kirana stock items
    using the LightGBM machine learning model (`negotiation_lgb_model.pkl`).
    """
    try:
        result = prediction_service.predict_selling_price(
            turn_number=request.turn_number,
            kirana_historical_trust_score=request.kirana_historical_trust_score,
            distributor_credit_limit_allocated=request.distributor_credit_limit_allocated,
            current_turn_offer_price=request.current_turn_offer_price,
            price_elasticity_demanded=request.price_elasticity_demanded,
            sentiment_intensity_score=request.sentiment_intensity_score,
            geographic_tier=request.geographic_tier,
            state_context=request.state_context,
            commodity_type=request.commodity_type,
            negotiation_posture=request.negotiation_posture,
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction service error: {str(e)}"
        )

@router.get("/model-info")
async def get_model_info():
    """
    Check the status and metadata of the selling prediction LightGBM model.
    """
    return {
        "model_loaded": prediction_service.is_loaded,
        "model_type": "LGBMRegressor",
        "model_file": "negotiation_lgb_model.pkl",
        "features": [
            "turn_number",
            "kirana_historical_trust_score",
            "distributor_credit_limit_allocated",
            "current_turn_offer_price",
            "price_elasticity_demanded",
            "sentiment_intensity_score",
            "geographic_tier",
            "state_context",
            "commodity_type",
            "negotiation_posture"
        ]
    }
