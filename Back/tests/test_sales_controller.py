import pytest
from fastapi import status
from modules.catalog.models.product import Product
from modules.catalog.models.stock import Stock

@pytest.fixture
def sample_products(db_session):
    prod1 = Product(nombre="Prod 1", precio=100.0, activo=True)
    db_session.add(prod1)
    db_session.commit()
    db_session.refresh(prod1)
    
    stock1 = Stock(product_id=prod1.id, cantidad=10)
    db_session.add(stock1)
    
    prod2 = Product(nombre="Prod 2", precio=200.0, activo=True)
    db_session.add(prod2)
    db_session.commit()
    db_session.refresh(prod2)
    
    stock2 = Stock(product_id=prod2.id, cantidad=5)
    db_session.add(stock2)
    
    db_session.commit()
    return prod1, prod2

def test_checkout_success(auth_client, sample_products):
    client, user = auth_client
    prod1, prod2 = sample_products
    
    payload = {
        "items": [
            {"product_id": prod1.id, "cantidad": 2},
            {"product_id": prod2.id, "cantidad": 1}
        ],
        "direccion_entrega": "Calle Falsa 123, Mar del Plata"
    }
    
    response = client.post("/cart/checkout", json=payload)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["total"] == 400.0 # 100*2 + 200*1
    assert len(data["items"]) == 2
    assert "orden_id" in data

def test_checkout_insufficient_stock(auth_client, sample_products):
    client, user = auth_client
    prod1, _ = sample_products
    
    payload = {
        "items": [
            {"product_id": prod1.id, "cantidad": 100}
        ],
        "direccion_entrega": "Calle Falsa 123, Mar del Plata"
    }
    
    response = client.post("/cart/checkout", json=payload)
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "stock" in response.json()["detail"].lower()

def test_checkout_invalid_product(auth_client):
    client, user = auth_client
    
    payload = {
        "items": [
            {"product_id": 9999, "cantidad": 1}
        ],
        "direccion_entrega": "Calle Falsa 123, Mar del Plata"
    }
    
    response = client.post("/cart/checkout", json=payload)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
