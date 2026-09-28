from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
import uuid
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import KiranaAPIException, NotFoundException, ConflictException
from app.db.models.user import User
from app.db.models.shop import Shop
from app.db.models.product import Product
from app.db.models.inventory import Inventory, InventoryMovement, MovementType
from app.db.models.sale import Sale, SaleItem, PaymentMethod, PaymentStatus
from app.db.models.customer import Customer
from app.db.models.khata import KhataAccount, KhataTransaction, KhataTransactionType
from app.db.models.audit import AuditLog
from app.schemas.sale import SaleCreate


class SalesService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_sale(self, shop_id: UUID, current_user: User, sale_in: SaleCreate) -> Sale:
        async with self.db.begin_nested():
            # Generate invoice number if missing
            invoice_number = sale_in.invoice_number or f"INV-{int(datetime.now().timestamp())}-{uuid.uuid4().hex[:4].upper()}"

            # Calculate totals
            subtotal = Decimal("0.00")
            tax_total = Decimal("0.00")
            item_data_list = []

            for item in sale_in.items:
                res = await self.db.execute(
                    select(Product).where(
                        Product.id == item.product_id,
                        Product.shop_id == shop_id,
                        Product.is_active == True
                    )
                )
                product = res.scalar_one_or_none()
                if not product:
                    raise NotFoundException(f"Product {item.product_id} not found or inactive in this shop")

                # Check inventory
                inv_res = await self.db.execute(
                    select(Inventory).where(
                        Inventory.product_id == product.id,
                        Inventory.shop_id == shop_id
                    )
                )
                inventory = inv_res.scalar_one_or_none()
                if not inventory:
                    raise NotFoundException(f"Inventory record missing for product {product.name}")

                available_qty = inventory.quantity - inventory.reserved_quantity
                if available_qty < item.quantity:
                    raise ConflictException(f"Insufficient stock for product '{product.name}'. Required: {item.quantity}, Available: {available_qty}")

                line_subtotal = item.quantity * item.unit_price - item.discount
                line_tax = line_subtotal * (item.tax_rate / Decimal("100.00"))
                line_total = line_subtotal + line_tax

                subtotal += line_subtotal
                tax_total += line_tax

                item_data_list.append({
                    "product": product,
                    "inventory": inventory,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "discount": item.discount,
                    "tax_rate": item.tax_rate,
                    "line_total": line_total
                })

            total_amount = subtotal + tax_total - sale_in.discount_amount

            # 1. Create Sale Header
            sale = Sale(
                shop_id=shop_id,
                customer_id=sale_in.customer_id,
                invoice_number=invoice_number,
                sale_date=sale_in.sale_date or datetime.now(timezone.utc),
                subtotal=subtotal,
                tax_amount=tax_total,
                discount_amount=sale_in.discount_amount,
                total_amount=total_amount,
                payment_method=sale_in.payment_method,
                payment_status=sale_in.payment_status,
                notes=sale_in.notes,
                created_by=current_user.id
            )
            self.db.add(sale)
            await self.db.flush()

            # 2. Create Items & Deduct Inventory
            for d in item_data_list:
                sale_item = SaleItem(
                    sale_id=sale.id,
                    product_id=d["product"].id,
                    quantity=d["quantity"],
                    unit_price=d["unit_price"],
                    discount=d["discount"],
                    tax_rate=d["tax_rate"],
                    total=d["line_total"]
                )
                self.db.add(sale_item)

                # Inventory update
                d["inventory"].quantity -= d["quantity"]
                d["inventory"].last_sold_at = datetime.now(timezone.utc)

                # Movement log
                movement = InventoryMovement(
                    shop_id=shop_id,
                    product_id=d["product"].id,
                    movement_type=MovementType.SALE,
                    quantity=d["quantity"],
                    unit_cost=d["inventory"].average_cost,
                    reference_type="SALE",
                    reference_id=sale.id,
                    notes=f"POS Sale Invoice {invoice_number}",
                    created_by=current_user.id
                )
                self.db.add(movement)

            # 3. Khata Ledger handling for CREDIT transactions
            if sale_in.payment_method == PaymentMethod.CREDIT or sale_in.payment_status == PaymentStatus.PENDING:
                if not sale_in.customer_id:
                    raise ConflictException("Customer is required for credit/Khata sales")

                khata_res = await self.db.execute(
                    select(KhataAccount).where(
                        KhataAccount.shop_id == shop_id,
                        KhataAccount.customer_id == sale_in.customer_id
                    )
                )
                khata_account = khata_res.scalar_one_or_none()
                if not khata_account:
                    khata_account = KhataAccount(
                        shop_id=shop_id,
                        customer_id=sale_in.customer_id,
                        current_balance=Decimal("0.00")
                    )
                    self.db.add(khata_account)
                    await self.db.flush()

                khata_account.current_balance += total_amount

                khata_tx = KhataTransaction(
                    shop_id=shop_id,
                    khata_account_id=khata_account.id,
                    transaction_type=KhataTransactionType.CREDIT,
                    amount=total_amount,
                    reference_type="SALE",
                    reference_id=sale.id,
                    description=f"Credit Sale - Invoice #{invoice_number}",
                    created_by=current_user.id
                )
                self.db.add(khata_tx)

            # 4. Audit Log
            audit = AuditLog(
                shop_id=shop_id,
                user_id=current_user.id,
                action="SALE_CREATED",
                entity_type="Sale",
                entity_id=str(sale.id),
                new_values={"invoice_number": invoice_number, "total_amount": str(total_amount)}
            )
            self.db.add(audit)

        await self.db.commit()
        res = await self.db.execute(
            select(Sale)
            .options(selectinload(Sale.items))
            .where(Sale.id == sale.id)
        )
        return res.scalar_one()

    async def get_sales(self, shop_id: UUID, skip: int = 0, limit: int = 20) -> List[Sale]:
        res = await self.db.execute(
            select(Sale)
            .options(selectinload(Sale.items))
            .where(Sale.shop_id == shop_id)
            .order_by(Sale.sale_date.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(res.scalars().all())

    async def get_sale_by_id(self, shop_id: UUID, sale_id: UUID) -> Optional[Sale]:
        res = await self.db.execute(
            select(Sale)
            .options(selectinload(Sale.items))
            .where(
                Sale.id == sale_id,
                Sale.shop_id == shop_id
            )
        )
        return res.scalar_one_or_none()
