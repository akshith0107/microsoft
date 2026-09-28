from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Any, Optional
from app.core.config import settings
from app.core.logging import logger


class WeatherClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.WEATHER_API_KEY

    async def get_current_weather(self, location_name: str = "Delhi") -> Dict[str, Any]:
        logger.info("Fetching Weather Data", location=location_name)
        return {
            "location_name": location_name,
            "latitude": Decimal("28.6139"),
            "longitude": Decimal("77.2090"),
            "observed_at": datetime.now(timezone.utc),
            "temperature_c": Decimal("34.50"),
            "humidity": Decimal("65.00"),
            "precipitation_mm": Decimal("0.00"),
            "precipitation_probability": Decimal("10.00"),
            "weather_condition": "Sunny & Hot",
            "source": "OpenWeather"
        }
