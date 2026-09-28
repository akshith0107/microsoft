import pytest
import uuid
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_unauthorized_shop_access_rejected(client: AsyncClient, seed_data: dict):
    fake_shop_id = str(uuid.uuid4())
    headers = {"Authorization": seed_data["headers"]["Authorization"], "X-Shop-Id": fake_shop_id}

    response = await client.get("/api/v1/products", headers=headers)
    assert response.status_code == 403
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "FORBIDDEN"
