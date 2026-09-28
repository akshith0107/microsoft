import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_signup_success(client: AsyncClient):
    payload = {
        "name": "New Owner",
        "email": "newowner@test.com",
        "phone": "+919111122222",
        "password": "SecurePassword123!",
        "shop_name": "New Kirana Store",
        "preferred_language": "en"
    }
    response = await client.post("/api/v1/auth/signup", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert data["data"]["shop_id"] is not None


@pytest.mark.asyncio
async def test_signup_duplicate_email(client: AsyncClient, seed_data: dict):
    payload = {
        "name": "Duplicate User",
        "email": "owner@test.com",
        "password": "SecurePassword123!",
        "shop_name": "Duplicate Store"
    }
    response = await client.post("/api/v1/auth/signup", json=payload)
    assert response.status_code == 409
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "CONFLICT"


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, seed_data: dict):
    payload = {
        "email": "owner@test.com",
        "password": "TestPassword123!"
    }
    response = await client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, seed_data: dict):
    payload = {
        "email": "owner@test.com",
        "password": "WrongPassword!"
    }
    response = await client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
