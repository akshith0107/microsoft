from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Dict, Any, List
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.product import Product
from app.db.models.inventory import Inventory
from app.db.models.sale import Sale, SaleItem


async def extract_product_features(db: AsyncSession, shop_id: UUID, product_id: UUID) -> Dict[str, Any]:
    now = datetime.now(timezone.utc)
    d1 = now - timedelta(days=1)
    d7 = now - timedelta(days=7)
    d14 = now - timedelta(days=14)
    d30 = now - timedelta(days=30)

    # Fetch product and inventory
    p_res = await db.execute(select(Product).where(Product.id == product_id, Product.shop_id == shop_id))
    product = p_res.scalar_one_or_none()
    if not product:
        return {}

    inv_res = await db.execute(select(Inventory).where(Inventory.product_id == product_id, Inventory.shop_id == shop_id))
    inventory = inv_res.scalar_one_or_none()
    current_stock = float(inventory.quantity) if inventory else 0.0

    # Sales aggregations
    async def get_sales_sum(start_dt: datetime) -> float:
        res = await db.execute(
            select(func.coalesce(func.sum(SaleItem.quantity), 0))
            .join(Sale, SaleItem.sale_id == Sale.id)
            .where(
                Sale.shop_id == shop_id,
                SaleItem.product_id == product_id,
                Sale.sale_date >= start_dt
            )
        )
        val = res.scalar_one()
        return float(val)

    sales_1d = await get_sales_sum(d1)
    sales_7d = await get_sales_sum(d7)
    sales_14d = await get_sales_sum(d14)
    sales_30d = await get_sales_sum(d30)

    daily_avg_7d = sales_7d / 7.0
    daily_avg_30d = sales_30d / 30.0

    # Stock coverage in days
    stock_coverage_days = (current_stock / daily_avg_7d) if daily_avg_7d > 0 else 999.0

    # Sales growth trend: (7d_rate vs previous_7d_rate)
    prev_7d_sales = max(0.0, sales_14d - sales_7d)
    sales_growth = ((sales_7d - prev_7d_sales) / prev_7d_sales) if prev_7d_sales > 0 else 0.0

    return {
        "product_id": str(product_id),
        "product_name": product.name,
        "sku": product.sku,
        "current_stock": current_stock,
        "reorder_level": float(product.reorder_level),
        "target_stock": float(product.target_stock),
        "sales_1d": sales_1d,
        "sales_7d": sales_7d,
        "sales_14d": sales_14d,
        "sales_30d": sales_30d,
        "daily_avg_7d": daily_avg_7d,
        "daily_avg_30d": daily_avg_30d,
        "stock_coverage_days": stock_coverage_days,
        "sales_growth": sales_growth,
    }
