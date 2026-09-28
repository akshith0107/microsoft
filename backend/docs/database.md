# Kirana AI Backend — Database Architecture

## 1. Principles

- **PostgreSQL 16+**: Authoritative source of truth for business data.
- **UUID Primary Keys**: Every entity uses UUIDv4 primary keys.
- **Precision**: Money uses `NUMERIC(12,2)`. Quantities use `NUMERIC(12,3)`. Floating point for currency is strictly prohibited.
- **Multi-Tenancy**: Every shop-specific table includes `shop_id` foreign key.
- **Immutability & History**: Sales, purchases, khata transactions, and inventory movements are append-only historical ledgers.

---

## 2. Table Indexing & Performance

The schema incorporates indexes for query optimization:
- `products`: `(shop_id)`, `(shop_id, sku)`, `(shop_id, barcode)`, `(name)`
- `inventory`: `(shop_id, product_id)`
- `sales`: `(shop_id, sale_date)`, `(invoice_number)`
- `sale_items`: `(sale_id)`, `(product_id)`
- `purchases`: `(shop_id, purchase_date)`
- `khata_accounts`: `(shop_id, customer_id)`
- `khata_transactions`: `(shop_id, khata_account_id, transaction_date)`
- `recommendations`: `(shop_id, status)`, `(generated_at)`
