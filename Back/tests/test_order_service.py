import pytest
from modules.orders.services.order_service import OrderService, TransicionEstadoInvalidaError
from modules.orders.models.order import Order, OrderEstado

@pytest.fixture
def sample_order(db_session):
    from modules.auth.models.user import User, UserRole
    user = User(nombre="Test", apellido="User", email="test_order@email.com", password_hash="hash", role=UserRole.CLIENTE)
    db_session.add(user)
    db_session.commit()
    
    order = Order(user_id=user.id, total=100.0, direccion_entrega="Direccion", estado=OrderEstado.PENDIENTE)
    db_session.add(order)
    db_session.commit()
    return order

def test_cambiar_estado_valido(db_session, sample_order):
    service = OrderService(db_session)
    # PENDIENTE -> EN_PREPARACION
    service.cambiar_estado(sample_order.id, OrderEstado.EN_PREPARACION)
    assert sample_order.estado == OrderEstado.EN_PREPARACION
    
    # EN_PREPARACION -> PREPARADO
    service.cambiar_estado(sample_order.id, OrderEstado.PREPARADO)
    assert sample_order.estado == OrderEstado.PREPARADO

def test_cambiar_estado_invalido(db_session, sample_order):
    service = OrderService(db_session)
    # PENDIENTE -> DESPACHADO (Salteando pasos)
    with pytest.raises(TransicionEstadoInvalidaError):
        service.cambiar_estado(sample_order.id, OrderEstado.DESPACHADO)
