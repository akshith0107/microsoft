import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
from decimal import Decimal

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings
from app.core.security import get_password_hash
from app.db.base import Base
from app.db.models.user import User
from app.db.models.shop import Shop, ShopMember, Role
from app.db.models.category import Category
from app.db.models.product import Product, Unit
from app.db.models.inventory import Inventory, InventoryMovement, MovementType
from app.db.models.customer import Customer
from app.db.models.supplier import Supplier
from app.db.models.purchase import Purchase, PurchaseItem, PaymentStatus as PurchasePaymentStatus
from app.db.models.sale import Sale, SaleItem, PaymentMethod, PaymentStatus as SalePaymentStatus
from app.db.models.khata import KhataAccount, KhataTransaction, KhataTransactionType
from app.db.models.expense import ExpenseCategory, Expense
from app.db.models.complaint import Complaint, ComplaintStatus, ComplaintPriority
from app.db.models.order import Order, OrderItem, OrderType, OrderStatus
from app.db.models.recommendation import Recommendation, RecommendationOutcome, RecommendationType, RecommendationStatus, DecisionType, OutcomeType
from app.db.models.conversation import Conversation, ConversationMessage, MessageRole, MessageType
from app.db.models.voice import VoiceInteraction
from app.db.models.receipt import ReceiptScan, ReceiptScanItem, OCRProcessingStatus


async def seed_database():
    print("Starting database seeding...")
    db_url = settings.DATABASE_URL
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif db_url.startswith("sqlite://") and not db_url.startswith("sqlite+aiosqlite://"):
        db_url = db_url.replace("sqlite://", "sqlite+aiosqlite://", 1)

    engine_kwargs = {}
    if "sqlite" in db_url:
        engine_kwargs["connect_args"] = {"check_same_thread": False}

    engine = create_async_engine(db_url, **engine_kwargs)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        # 1. Users
        pwd_hash = get_password_hash("ChangeMe123!")

        owner = User(
            name="Rajesh Kumar",
            email="owner@sharmastore.com",
            phone="+919876543210",
            password_hash=pwd_hash,
            preferred_language="hinglish",
            is_active=True,
            email_verified=True,
            phone_verified=True
        )
        staff = User(
            name="Amit Kumar",
            email="staff@sharmastore.com",
            phone="+919876543211",
            password_hash=pwd_hash,
            preferred_language="hi",
            is_active=True
        )
        session.add_all([owner, staff])
        await session.flush()

        # 2. Shop & Members
        shop = Shop(
            name="Sharma General Store",
            owner_id=owner.id,
            phone="+919876543210",
            email="owner@sharmastore.com",
            address_line1="12, Main Market Road",
            city="New Delhi",
            state="Delhi",
            pincode="110001",
            country="IN",
            currency="INR",
            timezone="Asia/Kolkata"
        )
        session.add(shop)
        await session.flush()

        m1 = ShopMember(shop_id=shop.id, user_id=owner.id, role=Role.OWNER, is_active=True)
        m2 = ShopMember(shop_id=shop.id, user_id=staff.id, role=Role.STAFF, is_active=True)
        session.add_all([m1, m2])

        # 3. Categories
        cat_groceries = Category(shop_id=shop.id, name="Groceries & Staples", description="Essential daily cooking items")
        cat_snacks = Category(shop_id=shop.id, name="Snacks & Beverages", description="Instant noodles, biscuits, and cold drinks")
        cat_personal = Category(shop_id=shop.id, name="Personal & Home Care", description="Soaps, detergents, and toothpaste")
        session.add_all([cat_groceries, cat_snacks, cat_personal])
        await session.flush()

        # 4. Products & Inventory
        products_data = [
            ("Maggi 2-Minute Noodles", "MAG-001", "890105800001", cat_snacks.id, Unit.packet, Decimal("12.00"), Decimal("14.00"), Decimal("50.000"), Decimal("10.000")),
            ("Parle-G 80g", "PAR-002", "890105800002", cat_snacks.id, Unit.packet, Decimal("4.20"), Decimal("5.00"), Decimal("100.000"), Decimal("20.000")),
            ("Amul Taaza Milk 500ml", "AMU-003", "890105800003", cat_groceries.id, Unit.packet, Decimal("26.00"), Decimal("27.00"), Decimal("30.000"), Decimal("5.000")),
            ("Tata Salt 1kg", "TAT-004", "890105800004", cat_groceries.id, Unit.packet, Decimal("24.00"), Decimal("28.00"), Decimal("40.000"), Decimal("10.000")),
            ("Aashirvaad Atta 5kg", "AAS-005", "890105800005", cat_groceries.id, Unit.packet, Decimal("210.00"), Decimal("240.00"), Decimal("15.000"), Decimal("3.000")),
            ("Britannia Good Day", "BRI-006", "890105800006", cat_snacks.id, Unit.packet, Decimal("25.00"), Decimal("30.00"), Decimal("40.000"), Decimal("8.000")),
            ("Coca-Cola 750ml", "COC-007", "890105800007", cat_snacks.id, Unit.bottle, Decimal("38.00"), Decimal("45.00"), Decimal("25.000"), Decimal("5.000")),
            ("Thums Up 750ml", "THU-008", "890105800008", cat_snacks.id, Unit.bottle, Decimal("38.00"), Decimal("45.00"), Decimal("25.000"), Decimal("5.000")),
            ("Surf Excel Easy Wash 1kg", "SUR-009", "890105800009", cat_personal.id, Unit.packet, Decimal("130.00"), Decimal("150.00"), Decimal("12.000"), Decimal("3.000")),
            ("Fortune Sunflower Oil 1L", "FOR-010", "890105800010", cat_groceries.id, Unit.pouch, Decimal("135.00"), Decimal("155.00"), Decimal("20.000"), Decimal("5.000")),
            ("Colgate Strong Teeth 100g", "COL-011", "890105800011", cat_personal.id, Unit.box, Decimal("55.00"), Decimal("65.00"), Decimal("18.000"), Decimal("4.000")),
            ("Dettol Original Soap 75g", "DET-012", "890105800012", cat_personal.id, Unit.piece, Decimal("32.00"), Decimal("38.00"), Decimal("30.000"), Decimal("6.000")),
        ]

        seeded_products = []
        for name, sku, bc, cat_id, unit_val, p_price, s_price, stock_qty, reorder_lvl in products_data:
            p = Product(
                shop_id=shop.id,
                category_id=cat_id,
                sku=sku,
                barcode=bc,
                name=name,
                unit=unit_val,
                purchase_price=p_price,
                selling_price=s_price,
                reorder_level=reorder_lvl,
                target_stock=stock_qty * Decimal("2.0"),
                is_active=True
            )
            session.add(p)
            await session.flush()
            seeded_products.append(p)

            inv = Inventory(
                shop_id=shop.id,
                product_id=p.id,
                quantity=stock_qty,
                average_cost=p_price,
                last_purchase_price=p_price,
                last_restocked_at=datetime.now(timezone.utc) - timedelta(days=5)
            )
            session.add(inv)

        # 5. Customers & Suppliers
        c1 = Customer(shop_id=shop.id, name="Suresh Gupta", phone="+919811122233", credit_limit=Decimal("5000.00"))
        c2 = Customer(shop_id=shop.id, name="Ramesh Verma", phone="+919811122234", credit_limit=Decimal("3000.00"))
        c3 = Customer(shop_id=shop.id, name="Pooja Sharma", phone="+919811122235", credit_limit=Decimal("2000.00"))
        session.add_all([c1, c2, c3])
        await session.flush()

        sup1 = Supplier(shop_id=shop.id, name="Delhi Wholesale Traders", phone="+911123456789", average_lead_time_days=2)
        sup2 = Supplier(shop_id=shop.id, name="FMCG Distributors Co.", phone="+911123456790", average_lead_time_days=3)
        session.add_all([sup1, sup2])
        await session.flush()

        # 6. Historical Sales (30 Days non-uniform)
        now = datetime.now(timezone.utc)
        for days_back in range(30, 0, -1):
            sale_date = now - timedelta(days=days_back)
            is_weekend = sale_date.weekday() >= 5
            num_sales = 4 if is_weekend else 2

            for s_idx in range(num_sales):
                inv_num = f"INV-{int(sale_date.timestamp())}-{s_idx}"
                cust = c1 if (s_idx % 2 == 0) else c2

                maggi = seeded_products[0]
                colacola = seeded_products[6]
                qty_m = Decimal("4.000") if is_weekend else Decimal("2.000")
                qty_c = Decimal("3.000") if is_weekend else Decimal("1.000")

                tot_m = qty_m * maggi.selling_price
                tot_c = qty_c * colacola.selling_price
                tot_sale = tot_m + tot_c

                sale = Sale(
                    shop_id=shop.id,
                    customer_id=cust.id,
                    invoice_number=inv_num,
                    sale_date=sale_date,
                    subtotal=tot_sale,
                    tax_amount=Decimal("0.00"),
                    discount_amount=Decimal("0.00"),
                    total_amount=tot_sale,
                    payment_method=PaymentMethod.CASH if s_idx == 0 else PaymentMethod.CREDIT,
                    payment_status=SalePaymentStatus.PAID if s_idx == 0 else SalePaymentStatus.PENDING,
                    created_by=owner.id
                )
                session.add(sale)
                await session.flush()

                item1 = SaleItem(sale_id=sale.id, product_id=maggi.id, quantity=qty_m, unit_price=maggi.selling_price, total=tot_m)
                item2 = SaleItem(sale_id=sale.id, product_id=colacola.id, quantity=qty_c, unit_price=colacola.selling_price, total=tot_c)
                session.add_all([item1, item2])

        # 7. Khata Balances
        khata1 = KhataAccount(shop_id=shop.id, customer_id=c1.id, credit_limit=Decimal("5000.00"), current_balance=Decimal("1250.00"))
        khata2 = KhataAccount(shop_id=shop.id, customer_id=c2.id, credit_limit=Decimal("3000.00"), current_balance=Decimal("450.00"))
        session.add_all([khata1, khata2])
        await session.flush()

        tx1 = KhataTransaction(
            shop_id=shop.id,
            khata_account_id=khata1.id,
            transaction_type=KhataTransactionType.CREDIT,
            amount=Decimal("1250.00"),
            description="Credit sale purchases ledger",
            transaction_date=now - timedelta(days=2),
            created_by=owner.id
        )
        session.add(tx1)

        # 8. Recommendations & Hindsight Memory test case
        rec = Recommendation(
            shop_id=shop.id,
            type=RecommendationType.STOCK,
            title="Maggi Stock Restock Recommendation",
            recommendation="Forecast shows weekend demand spike. Order 40 packets of Maggi.",
            reasoning="Sales increased 30% over weekends. Current stock covers ~4 days.",
            priority="HIGH",
            related_product_id=seeded_products[0].id,
            status=RecommendationStatus.ACCEPTED
        )
        session.add(rec)
        await session.flush()

        outcome = RecommendationOutcome(
            recommendation_id=rec.id,
            shop_id=shop.id,
            decision=DecisionType.MODIFIED,
            decision_notes="Ordered 30 packets instead of 40 based on shop limit preference.",
            outcome=OutcomeType.SUCCESS,
            outcome_notes="30 packets sold cleanly before next delivery.",
            created_by=owner.id
        )
        session.add(outcome)

        await session.commit()
        print("Database seeded cleanly with demo data!")


if __name__ == "__main__":
    asyncio.run(seed_database())
