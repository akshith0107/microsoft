import os
import pickle
import logging
from typing import Dict, Any, Optional
import pandas as pd

logger = logging.getLogger(__name__)

MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "negotiation_lgb_model.pkl")

class SellingPredictionService:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SellingPredictionService, cls).__new__(cls)
            cls._instance._load_model()
        return cls._instance

    def _load_model(self):
        if os.path.exists(MODEL_PATH):
            try:
                with open(MODEL_PATH, "rb") as f:
                    self._model = pickle.load(f)
                logger.info(f"Loaded LightGBM selling prediction model from {MODEL_PATH}")
            except Exception as e:
                logger.error(f"Failed to load LightGBM model from {MODEL_PATH}: {e}")
                self._model = None
        else:
            logger.warning(f"LightGBM model file not found at {MODEL_PATH}")
            self._model = None

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    def predict_selling_price(
        self,
        turn_number: int = 1,
        kirana_historical_trust_score: float = 0.85,
        distributor_credit_limit_allocated: float = 50000.0,
        current_turn_offer_price: float = 100.0,
        price_elasticity_demanded: float = -1.0,
        sentiment_intensity_score: float = 0.5,
        geographic_tier: int = 1,
        state_context: int = 1,
        commodity_type: int = 1,
        negotiation_posture: int = 1,
    ) -> Dict[str, Any]:
        features = {
            "turn_number": turn_number,
            "kirana_historical_trust_score": kirana_historical_trust_score,
            "distributor_credit_limit_allocated": distributor_credit_limit_allocated,
            "current_turn_offer_price": current_turn_offer_price,
            "price_elasticity_demanded": price_elasticity_demanded,
            "sentiment_intensity_score": sentiment_intensity_score,
            "geographic_tier": geographic_tier,
            "state_context": state_context,
            "commodity_type": commodity_type,
            "negotiation_posture": negotiation_posture,
        }

        if self._model is None:
            # Fallback heuristic calculation if model binary missing
            predicted_price = current_turn_offer_price * (1.0 + 0.02 * sentiment_intensity_score)
            return {
                "predicted_selling_price": round(predicted_price, 2),
                "features_used": features,
                "model_status": "fallback_heuristic",
            }

        df = pd.DataFrame([features])
        raw_pred = self._model.predict(df)[0]
        predicted_price = float(raw_pred)

        # Calculate estimated margin & recommended discount bounds
        suggested_min_price = round(predicted_price * 0.95, 2)
        suggested_max_price = round(predicted_price * 1.05, 2)

        return {
            "predicted_selling_price": round(predicted_price, 2),
            "suggested_min_price": suggested_min_price,
            "suggested_max_price": suggested_max_price,
            "features_used": features,
            "model_status": "lightgbm_negotiation_lgb_model",
        }


prediction_service = SellingPredictionService()
