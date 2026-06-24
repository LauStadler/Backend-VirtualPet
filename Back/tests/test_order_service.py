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

def test_solicitar_facturacion_exito(db_session, sample_order):
    service = OrderService(db_session)
    # CUIT de prueba válido (con guiones)
    cuit = "20-12345678-9"
    
    updated_order = service.solicitar_facturacion(
        order_id=sample_order.id,
        user_id=sample_order.user_id,
        cuit=cuit
    )
    
    assert updated_order.billing_cuit == "20123456789"
    assert updated_order.billing_requested_at is not None

def test_solicitar_facturacion_cuit_invalido(db_session, sample_order):
    service = OrderService(db_session)
    # CUIT inválido (corto)
    cuit = "123"
    
    with pytest.raises(ValueError) as exc:
        service.solicitar_facturacion(
            order_id=sample_order.id,
            user_id=sample_order.user_id,
            cuit=cuit
        )
    assert "no es válido" in str(exc.value)

def test_solicitar_facturacion_no_dueño(db_session, sample_order):
    service = OrderService(db_session)
    
    with pytest.raises(PermissionError) as exc:
        service.solicitar_facturacion(
            order_id=sample_order.id,
            user_id=9999, # ID de usuario ajeno
            cuit="20123456789"
        )
    assert "no pertenece a tu cuenta" in str(exc.value)

def test_solicitar_facturacion_cancelado(db_session, sample_order):
    service = OrderService(db_session)
    # Cancelar la orden primero
    sample_order.estado = OrderEstado.CANCELADO
    db_session.commit()
    
    with pytest.raises(ValueError) as exc:
        service.solicitar_facturacion(
            order_id=sample_order.id,
            user_id=sample_order.user_id,
            cuit="20123456789"
        )
    assert "cancelado" in str(exc.value)

def test_solicitar_facturacion_antiguo(db_session, sample_order):
    from datetime import datetime, timedelta
    service = OrderService(db_session)
    # Modificar la fecha de creación a hace 31 días
    sample_order.created_at = datetime.now() - timedelta(days=31)
    db_session.commit()
    
    with pytest.raises(ValueError) as exc:
        service.solicitar_facturacion(
            order_id=sample_order.id,
            user_id=sample_order.user_id,
            cuit="20123456789"
        )
    assert "más de 30 días" in str(exc.value)
