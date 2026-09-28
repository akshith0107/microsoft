import pytest
import uuid
from app.api.voice import parse_hinglish_quantities_and_products
from app.db.models.product import Product


def test_parse_hinglish_quantities_and_products():
    p1 = Product(id=uuid.uuid4(), name="Maggi 2-Min Masala Noodle 70g", brand="Nestle", selling_price=14, unit="packet")
    p2 = Product(id=uuid.uuid4(), name="Parle-G Gold Biscuits 100g", brand="Parle", selling_price=10, unit="packet")

    products = [p1, p2]

    # Test '2 Maggi aur 3 Parle-G'
    items = parse_hinglish_quantities_and_products("2 Maggi aur 3 Parle-G", products)
    assert len(items) == 2
    assert items[0]["quantity"] == 2
    assert items[1]["quantity"] == 3

    # Test Hindi number words 'do maggi, teen parle'
    items_hindi = parse_hinglish_quantities_and_products("do maggi aur teen parle", products)
    assert len(items_hindi) == 2
    assert items_hindi[0]["quantity"] == 2
    assert items_hindi[1]["quantity"] == 3
