# Kirana AI Backend — API Contract & Endpoint Reference

All API routes are served under `/api/v1`. OpenAPI specification is available interactively at `/api/v1/docs`.

---

## 1. Authentication Endpoints

- `POST /api/v1/auth/signup` — Register user, create shop, assign OWNER role, return JWT access token.
- `POST /api/v1/auth/login` — Authenticate user credentials, create session, return JWT access token.
- `POST /api/v1/auth/logout` — Revoke active session token.
- `GET /api/v1/auth/me` — Fetch authenticated user profile.
- `GET /api/v1/auth/shops` — List shops accessible by current user.

---

## 2. Multi-Tenant Header Scoping

All protected business queries require the `Authorization: Bearer <token>` header and the optional `X-Shop-Id: <shop_uuid>` header.

If `X-Shop-Id` is omitted, the API defaults to the user's primary active shop.

---

## 3. Core Business Operations

### Products & Inventory
- `GET /api/v1/products` — List active shop products with live inventory quantities.
- `POST /api/v1/products` — Create product and initialize stock record.
- `DELETE /api/v1/products/{id}` — Soft delete product (`is_active = false`).
- `GET /api/v1/inventory` — View inventory status and average costs.
- `POST /api/v1/inventory/{product_id}/adjust` — Post manual stock adjustment with movement audit log.

### Sales & POS Billing
- `POST /api/v1/sales` — Process POS checkout transaction. Validates stock, reduces inventory, logs stock movements, updates Khata ledger if CREDIT sale, and records audit log.

### Purchases & Supplier Restock
- `POST /api/v1/purchases` — Record supplier purchase. Increases inventory stock, recalculates weighted average cost, updates last purchase price, and logs stock movements.

### Khata / Udhaar Credit Ledger
- `GET /api/v1/khata` — List customer Khata accounts and outstanding balances.
- `POST /api/v1/khata/{customer_id}/payment` — Record customer balance payment.
- `GET /api/v1/customers/{id}/history` — Full customer ledger history, spend metrics, and complaints.

### Analytics & AI Assistant
- `GET /api/v1/dashboard` — Live dashboard metrics (sales, profit, expenses, low stock count, pending khata).
- `POST /api/v1/assistant/chat` — Multi-modal conversational assistant.
- `GET /api/v1/analytics/forecast/{product_id}` — 7-day demand forecasting and stockout risk analysis.
- `POST /api/v1/recommendations/{id}/decision` — Record owner decision and outcome learning.
