from fastapi import APIRouter

from app.api.health import router as health_router
from app.api.auth import router as auth_router
from app.api.shops import router as shops_router
from app.api.dashboard import router as dashboard_router
from app.api.categories import router as categories_router
from app.api.products import router as products_router
from app.api.inventory import router as inventory_router
from app.api.sales import router as sales_router
from app.api.purchases import router as purchases_router
from app.api.suppliers import router as suppliers_router
from app.api.customers import router as customers_router
from app.api.khata import router as khata_router
from app.api.expenses import router as expenses_router
from app.api.complaints import router as complaints_router
from app.api.orders import router as orders_router
from app.api.recommendations import router as recommendations_router
from app.api.conversations import router as conversations_router
from app.api.assistant import router as assistant_router
from app.api.voice import router as voice_router
from app.api.receipts import router as receipts_router
from app.api.analytics import router as analytics_router
from app.api.memory import router as memory_router
from app.api.weather import router as weather_router
from app.api.market import router as market_router

api_router = APIRouter()

# Root health endpoints
api_router.include_router(health_router)

# Domain API routers under /api/v1
api_router.include_router(auth_router)
api_router.include_router(shops_router)
api_router.include_router(dashboard_router)
api_router.include_router(categories_router)
api_router.include_router(products_router)
api_router.include_router(inventory_router)
api_router.include_router(sales_router)
api_router.include_router(purchases_router)
api_router.include_router(suppliers_router)
api_router.include_router(customers_router)
api_router.include_router(khata_router)
api_router.include_router(expenses_router)
api_router.include_router(complaints_router)
api_router.include_router(orders_router)
api_router.include_router(recommendations_router)
api_router.include_router(conversations_router)
api_router.include_router(assistant_router)
api_router.include_router(voice_router)
api_router.include_router(receipts_router)
api_router.include_router(analytics_router)
api_router.include_router(memory_router)
api_router.include_router(weather_router)
api_router.include_router(market_router)
