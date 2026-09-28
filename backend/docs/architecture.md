# Kirana AI Operating System — System Architecture

## 1. Overview

DukaanPulse (Kirana AI OS) is a production-grade, multi-tenant digital operating system designed for Indian Kirana and general retail store management. The Python/FastAPI backend acts as the central orchestration engine coordinating PostgreSQL business state, statistical ML demand forecasting, Hindsight long-term AI memory, and Gemini LLM natural language reasoning.

---

## 2. Technical Stack

- **Backend Framework**: Python 3.11+, FastAPI (Async API Orchestration)
- **Data Validation & Serialisation**: Pydantic v2, pydantic-settings
- **Database & ORM**: PostgreSQL 16+, SQLAlchemy 2.x AsyncSession, asyncpg
- **Database Migrations**: Alembic
- **Authentication & Security**: JWT Access Tokens, Argon2id & bcrypt password hashing
- **Testing**: pytest, pytest-asyncio, httpx, aiosqlite (in-memory test environment)
- **Integrations**: Hindsight AI Memory, Gemini 1.5 Pro, Sarvam AI Voice, Receipt OCR, OpenWeather, Agmarknet, WhatsApp Cloud API

---

## 3. Core Architecture & Separation of Concerns

```
[ React / Next.js Frontend ]
            │
            ▼
[ FastAPI Central Orchestration Engine ]
            │
  ┌─────────┼───────────┬──────────────┬──────────────┬──────────────┐
  │         │           │              │              │              │
  ▼         ▼           ▼              ▼              ▼              ▼
[Postgres] [Hindsight] [Gemini 1.5]  [ML Engine]   [Sarvam AI/OCR] [Weather/Market]
(Source    (Long-Term   (Reasoning &   (Demand        (Voice & Image (External
 of Truth)  Memory)      Hinglish)     Forecasting)    Processing)   APIs)
```

### Component Responsibilities:

1. **PostgreSQL 16+**: Authoritative **SOURCE OF TRUTH** for factual business records (Users, Shops, Products, Inventory, Sales, Khata Ledgers, Supplier Purchases, Expenses, Complaints, Audit Logs).
2. **FastAPI**: Multi-tenant RBAC enforcement, transactional business logic, REST APIs, and external client orchestration.
3. **ML Analytics Engine**: Calculates sales velocity, demand forecasts, stockout risks, and fast/slow movers using statistical moving averages and feature pipelines.
4. **Hindsight AI Memory**: Stores durable experiential memory (owner preferences, repeated business habits, historical recommendation outcomes).
5. **Gemini LLM**: Synthesizes factual DB state + ML forecasts + Hindsight memories into actionable Hinglish advice.
6. **External Integrations**: Sarvam AI (Voice STT/TTS), OCR (Invoice scanning), OpenWeather (Temperature/rain context), Agmarknet (Commodity price observations), WhatsApp (Supplier order dispatch).

---

## 4. Distinction: ML vs. Hindsight Memory vs. Gemini Reasoning

- **ML System**: Answers *"What is likely to happen quantitatively?"* (Demand numbers, sales velocity, stockout probability).
- **Hindsight System**: Answers *"What has this shop learned before?"* (Owner order caps, vendor reliability, past decision feedback).
- **Gemini Agent**: Answers *"What should we tell the shopkeeper, considering both?"* (Synthesizes factual numbers and past context into natural Hinglish explanations).
