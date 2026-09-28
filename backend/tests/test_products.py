import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_list_product(client: AsyncClient, seed_data: dict):
    headers = seed_data["headers"]
    payload = {
        "sku": "TEST-MAGGI-01",
        "barcode": "890105899999",
        "name": "Maggi Test Packet",
        "unit": "packet",
        "purchase_price": 12.00,
        "selling_price": 14.00,
        "tax_rate": 0.00,
        "reorder_level": 10.0,
        "target_stock": 50.0,
        "initial_stock": 25.0
    }

    create_resp = await client.post("/api/v1/products", json=payload, headers=headers)
    assert create_resp.status_code == 200
    p_data = create_resp.json()["data"]
    assert p_data["name"] == "Maggi Test Packet"
    assert float(p_data["current_stock"]) == 25.0

    list_resp = await client.get("/api/v1/products", headers=headers)
    assert list_resp.status_code == 200
    products = list_resp.json()["data"]
    assert len(products) == 1
    assert products[0]["sku"] == "TEST-MAGGI-01"
