import os
import uuid
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from infrastructure.db.base import Base
from modules.orders.services.order_service import OrderService
from modules.catalog.models.product import Product
from modules.catalog.models.stock import Stock
from modules.sales.schemas.sales_schema import CheckoutItemDetail
from modules.orders.models.order_item import OrderItem

@pytest.fixture
def db_engine():
    db_file = f"test_{uuid.uuid4().hex}.db"
    engine = create_engine(f"sqlite:///{db_file}")
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()
    if os.path.exists(db_file):
        os.remove(db_file)

@pytest.fixture
def session(db_engine):
    session_factory = sessionmaker(bind=db_engine)
    session = session_factory()
    yield session
    session.close()

def test_rollback_stock_on_payment_failure(session):
    """
    Si el pago falla, el stock descontado debe volver a su estado original (rollback).
    """
    # 1. Setup: Producto con stock 10
    product = Product(nombre="Producto Test Rollback", precio=100.0, activo=True)
    session.add(product)
    session.commit()
    product_id = product.id
    
    stock = Stock(product_id=product_id, cantidad=10)
    session.add(stock)
    session.commit()

    # 2. Forzar falla en el servicio de pagos
    from unittest.mock import patch
    with patch("modules.payments.services.payment_service.PaymentService.procesar") as mock_payment:
        mock_payment.side_effect = Exception("Error simulado de pasarela de pagos")
        
        service = OrderService(session)
        item = CheckoutItemDetail(
            product_id=product_id, 
            cantidad=3, 
            precio_unitario=100.0, 
            subtotal=300.0, 
            producto_nombre="Producto Test Rollback"
        )
        
        with pytest.raises(Exception):
            service.crear_orden(user_id=1, items=[item], total=300.0, direccion_entrega="Dir Test")

    # 3. Verificar que el stock SIGUE SIENDO 10
    session.expire_all()
    stock_actual = session.query(Stock).filter_by(product_id=product_id).first()
    assert stock_actual.cantidad == 10, f"El stock debería ser 10, pero quedó en {stock_actual.cantidad}"

def test_ignora_precio_inyectado_por_frontend(session):
    """
    El backend debe usar el precio de la DB, no el que mande el cliente en el body.
    """
    # 1. Setup: Producto cuesta 500.0 en DB
    product = Product(nombre="Producto Caro", precio=500.0, activo=True)
    session.add(product)
    session.commit()
    product_id = product.id
    session.add(Stock(product_id=product_id, cantidad=5))
    session.commit()

    # 2. Intento de compra mandando un precio de 1.0 (hack)
    service = OrderService(session)
    item_hackeado = CheckoutItemDetail(
        product_id=product_id, 
        cantidad=1, 
        precio_unitario=1.0, 
        subtotal=1.0,
        producto_nombre="Producto Caro"
    )

    # El servicio ahora debería ignorar el 1.0 y usar 500.0
    order = service.crear_orden(user_id=1, items=[item_hackeado], total=1.0, direccion_entrega="Dir Test")
    
    # 3. Verificar que el precio de la orden sea 500.0
    session.refresh(order)
    item_guardado = session.query(OrderItem).filter_by(order_id=order.id).first()
    
    assert item_guardado.precio_unitario == 500.0, f"¡ERROR! El sistema permitió inyectar precio: {item_guardado.precio_unitario}"
    assert order.total == 500.0, f"¡ERROR! El total de la orden es incorrecto: {order.total}"
