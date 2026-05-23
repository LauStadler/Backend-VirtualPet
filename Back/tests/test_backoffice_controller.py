import pytest
from fastapi import status
from modules.orders.models.order import OrderEstado

def test_backoffice_list_orders(admin_client, db_session):
    client, user = admin_client
    
    # Crear una orden manualmente para asegurar que hay algo que listar
    from modules.orders.models.order import Order
    order = Order(user_id=user.id, total=100.0, direccion_entrega="Direccion Admin")
    db_session.add(order)
    db_session.commit()
    
    response = client.get("/backoffice/orders")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1
    assert any(o["id"] == order.id for o in data)

def test_backoffice_change_order_status(admin_client, db_session):
    client, user = admin_client
    
    # Crear una orden
    from modules.orders.models.order import Order
    order = Order(user_id=user.id, total=100.0, direccion_entrega="Direccion Admin", estado=OrderEstado.PENDIENTE)
    db_session.add(order)
    db_session.commit()
    
    # Cambiar a PREPARADO (transición válida)
    payload = {"estado": OrderEstado.PREPARADO}
    response = client.patch(f"/backoffice/orders/{order.id}/estado", json=payload)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["estado"] == OrderEstado.PREPARADO

def test_backoffice_invalid_status_transition(admin_client, db_session):
    client, user = admin_client
    
    # Crear una orden
    from modules.orders.models.order import Order
    order = Order(user_id=user.id, total=100.0, direccion_entrega="Direccion Admin", estado=OrderEstado.PENDIENTE)
    db_session.add(order)
    db_session.commit()
    
    # Intentar saltar a ENVIADO (transición inválida desde PENDIENTE)
    payload = {"estado": OrderEstado.ENVIADO}
    response = client.patch(f"/backoffice/orders/{order.id}/estado", json=payload)
    
    assert response.status_code == status.HTTP_409_CONFLICT

def test_backoffice_unauthorized_access(auth_client):
    client, user = auth_client # Cliente regular, no admin
    
    response = client.get("/backoffice/orders")
    assert response.status_code == status.HTTP_403_FORBIDDEN
