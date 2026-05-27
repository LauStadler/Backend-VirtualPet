import pytest
from modules.payments.services.payment_service import PaymentService
from modules.payments.models.payment import PaymentEstado

def test_payment_service_procesar_success(db_session):
    # Setup: Necesitamos una orden existente para asociar el pago
    # Usamos una fixture o creamos una manualmente
    from modules.orders.models.order import Order
    from modules.auth.models.user import User, UserRole
    
    user = User(nombre="Test", apellido="User", email="test_pay@email.com", password_hash="hash", role=UserRole.CLIENTE)
    db_session.add(user)
    db_session.commit()
    
    orden = Order(user_id=user.id, total=150.0, direccion_entrega="Av. Falsa 123, Mar del Plata")
    db_session.add(orden)
    db_session.commit()
    
    service = PaymentService(db_session)
    payment = service.procesar(orden_id=orden.id, monto=150.0)
    
    assert payment is not None
    assert payment.orden_id == orden.id
    assert payment.monto == 150.0
    assert payment.estado == PaymentEstado.APROBADO
    assert payment.metodo == "simulado"
