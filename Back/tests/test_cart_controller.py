import pytest
from fastapi import status
from modules.catalog.models.product import Product

@pytest.fixture
def product_in_db(db_session):
    # Creamos un producto real y su stock para asegurar que el checkout pase
    from modules.catalog.models.stock import Stock
    prod = Product(nombre="Producto Test", precio=10.0, activo=True)
    db_session.add(prod)
    db_session.commit()
    
    stock = Stock(product_id=prod.id, cantidad=100)
    db_session.add(stock)
    db_session.commit()
    
    return prod

def test_checkout_success(auth_client, db_session, product_in_db):
    client, user = auth_client

    payload = {
        "items": [{"product_id": product_in_db.id, "cantidad": 1}],
        "direccion_entrega": "Calle Falsa 123, Mar del Plata"
    }

    response = client.post("/cart/checkout", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["orden_id"] is not None

def test_checkout_invalid_product(auth_client):
    client, user = auth_client

    payload = {
        "items": [{"product_id": 9999, "cantidad": 1}],
        "direccion_entrega": "Calle Falsa 123, Mar del Plata"
    }

    response = client.post("/cart/checkout", json=payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_checkout_duplicate_items(auth_client, product_in_db):
    client, user = auth_client

    payload = {
        "items": [
            {"product_id": product_in_db.id, "cantidad": 1},
            {"product_id": product_in_db.id, "cantidad": 2}
        ],
        "direccion_entrega": "Calle Falsa 123, Mar del Plata"
    }

    response = client.post("/cart/checkout", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
