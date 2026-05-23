import pytest
from modules.payments.services.payment_service import PaymentService
from modules.payments.models.payment import PaymentEstado

def test_procesar_pago_simulado(db_session):
    # Necesitamos una orden para asociar el pago
    from modules.auth.models.user import User, UserRole
    user = User(nombre="Test", apellido="User", email="test@email.com", password_hash="hash", role=UserRole.CLIENTE)
    db_session.add(user)
    db_session.commit()
    
    from modules.orders.models.order import Order
    order = Order(user_id=user.id, total=1000.0, direccion_entrega="Direccion")
    db_session.add(order)
    db_session.commit()
    
    service = PaymentService(db_session)
    payment = service.procesar(orden_id=order.id, monto=1000.0)
    
    assert payment.id is not None
    assert payment.orden_id == order.id
    assert payment.estado == PaymentEstado.APROBADO
    assert payment.monto == 1000.0
