import pytest
from fastapi import status
from modules.catalog.models.product import Product
from modules.catalog.models.stock import Stock

@pytest.fixture
def created_order(auth_client, db_session):
    client, user = auth_client
    
    # Crear producto y stock
    prod = Product(nombre="Prod Order", precio=500.0, activo=True)
    db_session.add(prod)
    db_session.commit()
    db_session.refresh(prod)
    stock = Stock(product_id=prod.id, cantidad=20)
    db_session.add(stock)
    db_session.commit()
    
    # Hacer checkout para crear orden
    payload = {
        "items": [{"product_id": prod.id, "cantidad": 2}],
        "direccion_entrega": "Calle Falsa 123, Mar del Plata"
    }
    response = client.post("/cart/checkout", json=payload)
    return response.json()["orden_id"]

def test_list_my_orders(auth_client, created_order):
    client, user = auth_client
    response = client.get("/orders")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1
    assert any(o["id"] == created_order for o in data)

def test_get_my_order_detail(auth_client, created_order):
    client, user = auth_client
    response = client.get(f"/orders/{created_order}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == created_order
    assert len(data["items"]) == 1
    assert data["items"][0]["producto_nombre"] == "Prod Order"

def test_get_other_user_order(auth_client, db_session):
    client, user = auth_client
    
    # Crear otra orden para otro usuario
    from modules.auth.models.user import User, UserRole
    other_user = User(nombre="Other", apellido="User", email="other@email.com", password_hash="hash", role=UserRole.CLIENTE)
    db_session.add(other_user)
    db_session.commit()
    
    from modules.orders.models.order import Order
    order = Order(user_id=other_user.id, total=100.0, direccion_entrega="Direccion")
    db_session.add(order)
    db_session.commit()
    
    response = client.get(f"/orders/{order.id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
