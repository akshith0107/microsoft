import os
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import settings

db_url = settings.DATABASE_URL
engine_kwargs = {"echo": False, "future": True}

if db_url.startswith("postgresql://") or db_url.startswith("postgresql+asyncpg://"):
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    parsed = urlparse(db_url)
    if parsed.query:
        query_params = parse_qs(parsed.query)
        has_ssl = any(k.lower() in ("sslmode", "ssl") for k in query_params)
        
        for unsupported_param in ["sslmode", "channel_binding", "gssencmode", "target_session_attrs"]:
            query_params.pop(unsupported_param, None)

        new_query = urlencode(query_params, doseq=True)
        db_url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))

        if has_ssl or "neon.tech" in db_url:
            engine_kwargs["connect_args"] = {"ssl": "require"}
    elif "neon.tech" in db_url:
        engine_kwargs["connect_args"] = {"ssl": "require"}

elif db_url.startswith("sqlite://") or "sqlite" in db_url:
    if not db_url.startswith("sqlite+aiosqlite://"):
        db_url = db_url.replace("sqlite://", "sqlite+aiosqlite://", 1)
    if "kirana.db" in db_url:
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        db_path = os.path.join(backend_dir, "kirana.db")
        db_url = f"sqlite+aiosqlite:///{db_path}"
    engine_kwargs["connect_args"] = {"check_same_thread": False}

async_engine = create_async_engine(db_url, **engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
