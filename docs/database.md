# Kirana OS — Database Architecture & Documentation

## 1. Architectural Principles

DukaanPulse (Kirana OS) is a production-grade, multi-tenant digital operating system for Indian Kirana and neighborhood retail store management.

The system is built on a clear separation of concerns:

- **PostgreSQL 16+**: The single, authoritative **SOURCE OF TRUTH** for factual business records (users, sessions, tokens, products, inventory, sales receipts, Khata ledgers, supplier purchases, expenses, complaints, and audit logs).
- **Hindsight**: The future long-term AI memory layer that retains shopkeeper preferences, past decisions, contextual habits, and recommendation feedback.
- **Python ML/Analytics Engine**: The future statistical service for demand forecasting, reorder point calculation, and price elasticity modelling.
- **LLM / Gemini Agent**: The future conversational and reasoning intelligence layer that synthesizes business context and generates actionable recommendations.

---

## 2. Authentication & Authorization Architecture

### 2.1 Authentication ("Who is the User?")
Canonical user accounts are stored in the `users` table:
- Password hashes use Argon2id or bcrypt. Plaintext passwords and secrets are **never** stored.
- Authentication sessions (`user_sessions`) use hashed session tokens with strict expiration and IP/User-Agent tracking.
- Password reset tokens (`password_reset_tokens`) and email verification tokens (`email_verification_tokens`) are single-use and hashed.
- Phone OTPs (`otp_verifications`) support `SIGNUP`, `LOGIN`, `PASSWORD_RESET`, and `PHONE_VERIFICATION` with attempt tracking and expiration.

### 2.2 Authorization ("What Shop can the User access?")
Multi-tenancy and permissions follow a strict RBAC model:

```
User (System Account)
  ↓
ShopMember (Role: OWNER | MANAGER | STAFF)
  ↓
Shop (Business Account)
  ↓
Shop Specific Business Records (Products, Inventory, Sales, Khata, Expenses)
```

- A user may belong to multiple shops through `shop_members`.
- Access permissions depend on the user's role in the active shop (`OWNER`, `MANAGER`, `STAFF`).
- Every shop-specific table contains a `shop_id` foreign key. All queries are strictly scoped by `shop_id` to guarantee tenant data isolation.

---

## 3. Entity Relationship Diagram (Mermaid)

```mermaid
erDiagram
    USER ||--o{ USER_SESSION : "has active"
    USER ||--o{ PASSWORD_RESET_TOKEN : "requests"
    USER ||--o{ EMAIL_VERIFICATION_TOKEN : "verifies"
    USER ||--o{ OTP_VERIFICATION : "receives"
    USER ||--o{ SHOP : "owns"
    USER ||--o{ SHOP_MEMBER : "belongs to"
    SHOP ||--o{ SHOP_MEMBER : "members"
    SHOP ||--o{ CATEGORY : "categories"
    SHOP ||--o{ PRODUCT : "catalogs"
    CATEGORY ||--o{ PRODUCT : "contains"
    PRODUCT ||--|| INVENTORY : "tracks stock"
    PRODUCT ||--o{ INVENTORY_MOVEMENT : "movements"
    SHOP ||--o{ SUPPLIER : "partners with"
    SUPPLIER ||--o{ PURCHASE : "supplies"
    PURCHASE ||--|{ PURCHASE_ITEM : "items"
    PRODUCT ||--o{ PURCHASE_ITEM : "bought"
    SHOP ||--o{ CUSTOMER : "serves"
    CUSTOMER ||--|| KHATA_ACCOUNT : "ledger"
    KHATA_ACCOUNT ||--o{ KHATA_TRANSACTION : "transactions"
    SHOP ||--o{ SALE : "records"
    CUSTOMER ||--o{ SALE : "buys"
    SALE ||--|{ SALE_ITEM : "items"
    PRODUCT ||--o{ SALE_ITEM : "sold"
    SHOP ||--o{ EXPENSE : "incurs"
    EXPENSE_CATEGORY ||--o{ EXPENSE : "classifies"
    SHOP ||--o{ COMPLAINT : "tracks"
    CUSTOMER ||--o{ COMPLAINT : "files"
    SHOP ||--o{ ORDER : "places"
    ORDER ||--|{ ORDER_ITEM : "items"
    SHOP ||--o{ RECOMMENDATION : "receives"
    RECOMMENDATION ||--o{ RECOMMENDATION_OUTCOME : "outcomes"
    SHOP ||--o{ CONVERSATION : "logs"
    CONVERSATION ||--o{ CONVERSATION_MESSAGE : "messages"
    USER ||--o{ VOICE_INTERACTION : "speaks"
    SHOP ||--o{ RECEIPT_SCAN : "scans"
    RECEIPT_SCAN ||--o{ RECEIPT_SCAN_ITEM : "items"
    PRODUCT ||--o{ PRODUCT_MARKET_MAPPING : "maps to Agmarknet"
    MARKET_PRICE_OBSERVATION ||--o{ PRODUCT_MARKET_MAPPING : "market price data"

    USER {
        uuid id PK
        string name
        string email UK
        string phone UK
        boolean is_active
        boolean email_verified
        boolean phone_verified
    }

    USER_SESSION {
        uuid id PK
        uuid user_id FK
        string session_token_hash UK
        timestamptz expires_at
    }

    SHOP {
        uuid id PK
        string name
        uuid owner_id FK
        string city
        string currency
    }

    SHOP_MEMBER {
        uuid id PK
        uuid shop_id FK
        uuid user_id FK
        enum role "OWNER | MANAGER | STAFF"
    }

    PRODUCT {
        uuid id PK
        uuid shop_id FK
        string sku
        string barcode
        string name
        decimal purchase_price
        decimal selling_price
    }

    INVENTORY {
        uuid id PK
        uuid shop_id FK
        uuid product_id FK
        decimal quantity
        decimal average_cost
    }

    SALE {
        uuid id PK
        uuid shop_id FK
        string invoice_number UK
        decimal total_amount
        string payment_method
    }

    KHATA_ACCOUNT {
        uuid id PK
        uuid shop_id FK
        uuid customer_id FK
        decimal current_balance
    }

    RECOMMENDATION {
        uuid id PK
        uuid shop_id FK
        string type
        string title
        string status
    }
```

---

## 4. Key Security & Data Integrity Controls

1. **Monetary Precision**: All financial fields (`price`, `total`, `subtotal`, `amount`, `balance`) use PostgreSQL `DECIMAL(12, 2)`. Floating-point numbers are strictly prohibited.
2. **Quantity Precision**: Inventory quantities use `DECIMAL(12, 3)` to accommodate fractional units (e.g., 2.500 kg).
3. **Auditability**: `inventory_movements` provides an append-only ledger for all stock additions (`PURCHASE`), deductions (`SALE`), damages (`DAMAGE`), and adjustments (`ADJUSTMENT_IN`, `ADJUSTMENT_OUT`).
4. **Soft Protection**: Financial history records (sales, purchases, khata transactions) are never physically deleted. Customer and product deletion is handled via `is_active = false`.
