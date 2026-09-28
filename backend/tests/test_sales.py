import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_pos_sale_checkout_flow(client: AsyncClient, seed_data: dict):
    headers = seed_data["headers"]

    # 1. Create Product
    prod_payload = {
        "sku": "POS-PARLE-01",
        "name": "Parle-G 80g",
        "unit": "packet",
        "purchase_price": 4.00,
        "selling_price": 5.00,
        "initial_stock": 50.0
    }
    prod_res = await client.post("/api/v1/products", json=prod_payload, headers=headers)
    product_id = prod_res.json()["data"]["id"]

    # 2. Process POS Sale
    sale_payload = {
        "payment_method": "CASH",
        "payment_status": "PAID",
        "items": [
            {
                "product_id": product_id,
                "quantity": 10.0,
                "unit_price": 5.00
            }
        ]
    }
    sale_res = await client.post("/api/v1/sales", json=sale_payload, headers=headers)
    assert sale_res.status_code == 200
    sale_data = sale_res.json()["data"]
    assert float(sale_data["total_amount"]) == 50.0

    # 3. Verify stock decreased to 40.0
    get_prod = await client.get(f"/api/v1/products/{product_id}", headers=headers)
    assert float(get_prod.json()["data"]["current_stock"]) == 40.0
