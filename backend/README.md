# Kirana AI Backend — FastAPI Orchestration Engine

Production-grade Python/FastAPI backend for an AI-powered Indian Kirana / general retail shop operating system.

---

## Quick Start

### 1. Set Up Virtual Environment

```bash
cd backend
python -m venv .venv

# On Windows PowerShell:
.\.venv\Scripts\activate

# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
```

### 3. Run Database Migrations

```bash
alembic upgrade head
```

### 4. Seed Development Database

```bash
python scripts/seed.py
```

### 5. Start Server

```bash
uvicorn app.main:app --reload --port 8000
```

Interactive API documentation will be available at:
`http://localhost:8000/api/v1/docs`

---

## Running Tests

```bash
pytest
```
