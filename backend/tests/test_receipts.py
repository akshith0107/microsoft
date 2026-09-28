import pytest
from httpx import AsyncClient

DUMMY_BASE64_IMAGE = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

@pytest.mark.asyncio
async def test_process_receipt_ocr_and_confirm_purchase(client: AsyncClient, seed_data: dict):
    headers = seed_data["headers"]

    # 1. Create a product SKU first so OCR matching can find it
    prod_payload = {
        "sku": "MAGGI-70G-01",
        "name": "Maggi 2-Minute Masala Noodles 70g",
        "unit": "packet",
        "purchase_price": 10.00,
        "selling_price": 14.00,
        "initial_stock": 10.0
    }
    prod_res = await client.post("/api/v1/products", json=prod_payload, headers=headers)
    assert prod_res.status_code == 200
    prod_id = prod_res.json()["data"]["id"]

    # 2. Process receipt upload
    process_payload = {
        "image_data": DUMMY_BASE64_IMAGE,
        "filename": "test_receipt.png"
    }
    scan_res = await client.post("/api/v1/receipts/process", json=process_payload, headers=headers)
    assert scan_res.status_code == 200
    scan_data = scan_res.json()["data"]
    receipt_id = scan_data["id"]
    assert scan_data["processing_status"] in ["review_required", "completed", "COMPLETED"]

    # 3. Confirm purchase order & restock inventory
    confirm_payload = {
        "invoice_number": "INV-TEST-9999",
        "supplier_id": None,
        "items": [
            {
                "product_id": prod_id,
                "extracted_name": "Maggi 2-Minute Masala Noodles 70g",
                "quantity": 20.0,
                "unit_price": 11.00
            }
        ]
    }
    confirm_res = await client.post(f"/api/v1/receipts/{receipt_id}/confirm", json=confirm_payload, headers=headers)
    assert confirm_res.status_code == 200
    confirm_data = confirm_res.json()["data"]
    assert confirm_data["invoice_number"] in ["GWT-1000", "INV-TEST-9999"]

    # 4. Verify stock increased from 10.0 to 30.0
    get_prod = await client.get(f"/api/v1/products/{prod_id}", headers=headers)
    assert get_prod.status_code == 200
    assert float(get_prod.json()["data"]["current_stock"]) == 30.0

@pytest.mark.asyncio
async def test_get_receipt_history(client: AsyncClient, seed_data: dict):
    headers = seed_data["headers"]

    # Process receipt upload
    process_payload = {
        "image_data": DUMMY_BASE64_IMAGE,
        "filename": "invoice_sample.jpg"
    }
    await client.post("/api/v1/receipts/process", json=process_payload, headers=headers)

    # Get receipt list
    history_res = await client.get("/api/v1/receipts", headers=headers)
    assert history_res.status_code == 200
    history_data = history_res.json()["data"]
    assert isinstance(history_data, list)
    assert len(history_data) >= 1

@pytest.mark.asyncio
async def test_process_receipt_unauthenticated(client: AsyncClient):
    res = await client.post("/api/v1/receipts/process", json={"image_data": DUMMY_BASE64_IMAGE})
    assert res.status_code in [401, 403]
