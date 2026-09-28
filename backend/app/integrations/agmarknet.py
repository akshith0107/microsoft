from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Any, List, Optional
from app.core.logging import logger


class AgmarknetClient:
    async def fetch_commodity_prices(self, commodity_name: str, state: str = "Delhi") -> List[Dict[str, Any]]:
        logger.info("Fetching Agmarknet Prices", commodity=commodity_name, state=state)
        return [
            {
                "commodity_name": commodity_name,
                "variety": "Common",
                "market_name": "Azadpur",
                "district": "North Delhi",
                "state": state,
                "arrival_date": datetime.now(timezone.utc),
                "min_price": Decimal("2400.00"),
                "max_price": Decimal("2800.00"),
                "modal_price": Decimal("2600.00"),
                "unit": "Quintal",
                "source": "Agmarknet"
            }
        ]
