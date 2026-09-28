from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
import uuid
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.db.models.user import User
from app.db.models.product import Product
from app.db.models.inventory import Inventory, InventoryMovement, MovementType
from app.db.models.purchase import Purchase, PurchaseItem
from app.db.models.audit import AuditLog
from app.schemas.purchase import PurchaseCreate


class PurchaseService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_purchase(self, shop_id: UUID, current_user: User, purchase_in: PurchaseCreate) -> Purchase:
        async with self.db.begin_nested():
            invoice_number = purchase_in.invoice_number or f"PO-{int(datetime.now().timestamp())}-{uuid.uuid4().hex[:4].upper()}"

            subtotal = Decimal("0.00")
            tax_total = Decimal("0.00")
            discount_total = Decimal("0.00")
            item_data_list = []

            for item in purchase_in.items:
                res = await self.db.execute(
                    select(Product).where(
                        Product.id == item.product_id,
                        Product.shop_id == shop_id,
                        Product.is_active == True
                    )
                )
                product = res.scalar_one_or_none()
                if not product:
                    raise NotFoundException(f"Product {item.product_id} not found in shop")

                inv_res = await self.db.execute(
                    select(Inventory).where(
                        Inventory.product_id == product.id,
                        Inventory.shop_id == shop_id
                    )
                )
                inventory = inv_res.scalar_one_or_none()
                if not inventory:
                    inventory = Inventory(
                        shop_id=shop_id,
                        product_id=product.id,
                        quantity=Decimal("0.000"),
                        average_cost=item.unit_cost
                    )
                    self.db.add(inventory)
                    await self.db.flush()

                line_subtotal = item.quantity * item.unit_cost - item.discount
                line_tax = line_subtotal * (item.tax_rate / Decimal("100.00"))
                line_total = line_subtotal + line_tax

                subtotal += line_subtotal
                tax_total += line_tax
                discount_total += item.discount

                item_data_list.append({
                    "product": product,
                    "inventory": inventory,
                    "quantity": item.quantity,
                    "unit_cost": item.unit_cost,
                    "tax_rate": item.tax_rate,
                    "discount": item.discount,
                    "line_total": line_total
                })

            total_amount = subtotal + tax_total

            # 1. Create Purchase
            purchase = Purchase(
                shop_id=shop_id,
                supplier_id=purchase_in.supplier_id,
                invoice_number=invoice_number,
                purchase_date=purchase_in.purchase_date or datetime.now(timezone.utc),
                subtotal=subtotal,
                tax_amount=tax_total,
                discount_amount=discount_total,
                total_amount=total_amount,
                payment_status=purchase_in.payment_status,
                notes=purchase_in.notes,
                created_by=current_user.id
            )
            self.db.add(purchase)
            await self.db.flush()

            # 2. Items, Stock & Weighted Average Cost
            for d in item_data_list:
                p_item = PurchaseItem(
                    purchase_id=purchase.id,
                    product_id=d["product"].id,
                    quantity=d["quantity"],
                    unit_cost=d["unit_cost"],
                    tax_rate=d["tax_rate"],
                    discount=d["discount"],
                    total=d["line_total"]
                )
                self.db.add(p_item)

                old_qty = d["inventory"].quantity
                old_cost = d["inventory"].average_cost
                added_qty = d["quantity"]
                unit_cost = d["unit_cost"]

                # Weighted Average Cost formula
                new_qty = old_qty + added_qty
                if new_qty > Decimal("0.000"):
                    new_avg_cost = ((old_qty * old_cost) + (added_qty * unit_cost)) / new_qty
                else:
                    new_avg_cost = unit_cost

                d["inventory"].quantity = new_qty
                d["inventory"].average_cost = new_avg_cost
                d["inventory"].last_purchase_price = unit_cost
                d["inventory"].last_restocked_at = datetime.now(timezone.utc)

                # Movement log
                movement = InventoryMovement(
                    shop_id=shop_id,
                    product_id=d["product"].id,
                    movement_type=MovementType.PURCHASE,
                    quantity=added_qty,
                    unit_cost=unit_cost,
                    reference_type="PURCHASE",
                    reference_id=purchase.id,
                    notes=f"Stock Restock PO #{invoice_number}",
                    created_by=current_user.id
                )
                self.db.add(movement)

            # Audit
            audit = AuditLog(
                shop_id=shop_id,
                user_id=current_user.id,
                action="PURCHASE_CREATED",
                entity_type="Purchase",
                entity_id=str(purchase.id),
                new_values={"invoice_number": invoice_number, "total_amount": str(total_amount)}
            )
            self.db.add(audit)

        await self.db.commit()
        res = await self.db.execute(
            select(Purchase)
            .options(selectinload(Purchase.items))
            .where(Purchase.id == purchase.id)
        )
        return res.scalar_one()

    async def get_purchases(self, shop_id: UUID, skip: int = 0, limit: int = 20) -> List[Purchase]:
        res = await self.db.execute(
            select(Purchase)
            .options(selectinload(Purchase.items))
            .where(Purchase.shop_id == shop_id)
            .order_by(Purchase.purchase_date.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(res.scalars().all())
