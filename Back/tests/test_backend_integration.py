import pytest
from fastapi import status
from modules.sales.schemas.sales_schema import CheckoutRequest, CartItemRequest
from modules.catalog.models.product import Product
from modules.catalog.models.stock import Stock
from modules.orders.models.order import OrderEstado

@pytest.fixture
def test_setup(db_session):
    # Crear producto con stock
    prod = Product(nombre="Product Integración", precio=100.0, activo=True)
    db_session.add(prod)
    db_session.commit()
    
    stock = Stock(product_id=prod.id, cantidad=10)
    db_session.add(stock)
    db_session.commit()
    
    return prod

def test_flujo_completo_checkout_y_pago(auth_client, db_session, test_setup):
    """
    Test de integración: 
    1. Realizar checkout.
    2. Verificar que se creó la orden.
    3. Verificar que se registró el pago.
    4. Verificar que se descontó el stock.
    """
    client, user = auth_client
    prod = test_setup
    
    # 1. Checkout
    payload = {
        "items": [{"product_id": prod.id, "cantidad": 3}],
        "direccion_entrega": "Calle de Integración 123, Mar del Plata"
    }
    
    response = client.post("/cart/checkout", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    orden_id = data["orden_id"]
    
    # 2. Verificar Orden en DB
    from modules.orders.models.order import Order
    orden = db_session.query(Order).filter(Order.id == orden_id).first()
    assert orden is not None
    assert orden.estado == OrderEstado.PENDIENTE
    assert orden.total == 300.0
    
    # 3. Verificar Pago en DB
    from modules.payments.models.payment import Payment, PaymentEstado
    pago = db_session.query(Payment).filter(Payment.orden_id == orden_id).first()
    assert pago is not None
    assert pago.estado == PaymentEstado.APROBADO
    assert pago.monto == 300.0
    
    # 4. Verificar Descuento de Stock
    # Nota: El stock debería haberse descontado al confirmar la orden
    db_session.refresh(prod.stock)
    assert prod.stock.cantidad == 7 # 10 - 3
