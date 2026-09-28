from datetime import datetime, time, timezone
from decimal import Decimal
from typing import Dict, Any, List
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.sale import Sale, SaleItem
from app.db.models.expense import Expense
from app.db.models.inventory import Inventory
from app.db.models.product import Product
from app.db.models.khata import KhataAccount
from app.db.models.complaint import Complaint, ComplaintStatus
from app.db.models.order import Order, OrderStatus
from app.db.models.recommendation import Recommendation, RecommendationStatus


class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_dashboard_summary(self, shop_id: UUID) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        today_start = datetime.combine(now.date(), time.min, tzinfo=timezone.utc)

        # 1. Today Sales & Revenue
        sales_res = await self.db.execute(
            select(
                func.coalesce(func.sum(Sale.total_amount), Decimal("0.00")),
                func.count(Sale.id)
            ).where(
                Sale.shop_id == shop_id,
                Sale.sale_date >= today_start
            )
        )
        today_sales, today_orders = sales_res.one()

        # 2. Today Expenses
        exp_res = await self.db.execute(
            select(
                func.coalesce(func.sum(Expense.amount), Decimal("0.00"))
            ).where(
                Expense.shop_id == shop_id,
                Expense.expense_date >= today_start
            )
        )
        today_expenses = exp_res.scalar_one()

        # 3. Today COGS & Profit
        cogs_res = await self.db.execute(
            select(
                func.coalesce(func.sum(SaleItem.quantity * Inventory.average_cost), Decimal("0.00"))
            )
            .join(Sale, SaleItem.sale_id == Sale.id)
            .join(Inventory, (Inventory.product_id == SaleItem.product_id) & (Inventory.shop_id == shop_id))
            .where(
                Sale.shop_id == shop_id,
                Sale.sale_date >= today_start
            )
        )
        today_cogs = cogs_res.scalar_one()
        today_profit = today_sales - today_cogs - today_expenses

        # 4. Inventory Value
        inv_val_res = await self.db.execute(
            select(
                func.coalesce(func.sum(Inventory.quantity * Inventory.average_cost), Decimal("0.00"))
            ).where(Inventory.shop_id == shop_id)
        )
        inventory_value = inv_val_res.scalar_one()

        # 5. Low Stock & Out of Stock counts
        low_stock_res = await self.db.execute(
            select(func.count(Product.id))
            .join(Inventory, Inventory.product_id == Product.id)
            .where(
                Product.shop_id == shop_id,
                Product.is_active == True,
                Inventory.quantity > Decimal("0.000"),
                Inventory.quantity <= Product.reorder_level
            )
        )
        low_stock_count = low_stock_res.scalar_one()

        out_stock_res = await self.db.execute(
            select(func.count(Product.id))
            .join(Inventory, Inventory.product_id == Product.id)
            .where(
                Product.shop_id == shop_id,
                Product.is_active == True,
                Inventory.quantity <= Decimal("0.000")
            )
        )
        out_of_stock_count = out_stock_res.scalar_one()

        # 6. Pending Khata Total
        khata_res = await self.db.execute(
            select(
                func.coalesce(func.sum(KhataAccount.current_balance), Decimal("0.00"))
            ).where(
                KhataAccount.shop_id == shop_id,
                KhataAccount.current_balance > Decimal("0.00")
            )
        )
        pending_khata = khata_res.scalar_one()

        # 7. Open Complaints
        complaint_res = await self.db.execute(
            select(func.count(Complaint.id)).where(
                Complaint.shop_id == shop_id,
                Complaint.status.in_([ComplaintStatus.OPEN, ComplaintStatus.IN_PROGRESS])
            )
        )
        open_complaints_count = complaint_res.scalar_one()

        # 8. Pending Supplier Orders
        order_res = await self.db.execute(
            select(func.count(Order.id)).where(
                Order.shop_id == shop_id,
                Order.status.in_([OrderStatus.DRAFT, OrderStatus.PENDING, OrderStatus.SENT, OrderStatus.CONFIRMED])
            )
        )
        pending_supplier_orders_count = order_res.scalar_one()

        # 9. Active Recommendations Count
        rec_res = await self.db.execute(
            select(func.count(Recommendation.id)).where(
                Recommendation.shop_id == shop_id,
                Recommendation.status == RecommendationStatus.NEW
            )
        )
        active_recommendations_count = rec_res.scalar_one()

        return {
            "today_sales": today_sales,
            "today_orders": today_orders,
            "today_expenses": today_expenses,
            "today_profit": today_profit,
            "inventory_value": inventory_value,
            "low_stock_count": low_stock_count,
            "out_of_stock_count": out_of_stock_count,
            "top_products": [],
            "slow_movers": [],
            "recent_sales": [],
            "recent_purchases": [],
            "pending_khata": pending_khata,
            "open_complaints_count": open_complaints_count,
            "pending_supplier_orders_count": pending_supplier_orders_count,
            "active_recommendations_count": active_recommendations_count
        }
