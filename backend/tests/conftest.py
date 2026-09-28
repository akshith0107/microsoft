import pytest
import pytest_asyncio
import sys
from pathlib import Path
from typing import AsyncGenerator

# Ensure backend directory is in sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.main import app
from app.db.base import Base
from app.db.session import get_async_db
from app.core.security import get_password_hash, create_access_token
from app.db.models.user import User
from app.db.models.shop import Shop, ShopMember, Role

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture(scope="function")
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def _override_get_db():
        yield test_db

    app.dependency_overrides[get_async_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def seed_data(test_db: AsyncSession):
    pwd_hash = get_password_hash("TestPassword123!")
    user = User(
        name="Test Owner",
        email="owner@test.com",
        phone="+919999999999",
        password_hash=pwd_hash,
        is_active=True
    )
    test_db.add(user)
    await test_db.flush()

    shop = Shop(
        name="Test Kirana Shop",
        owner_id=user.id,
        country="IN",
        currency="INR"
    )
    test_db.add(shop)
    await test_db.flush()

    member = ShopMember(
        shop_id=shop.id,
        user_id=user.id,
        role=Role.OWNER,
        is_active=True
    )
    test_db.add(member)
    await test_db.commit()

    token = create_access_token(user.id, extra_claims={"shop_id": str(shop.id)})

    return {
        "user": user,
        "shop": shop,
        "token": token,
        "headers": {"Authorization": f"Bearer {token}", "X-Shop-Id": str(shop.id)}
    }
