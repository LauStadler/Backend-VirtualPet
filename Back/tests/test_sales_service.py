import pytest
from modules.sales.services.sales_service import SalesService, ProductoInvalidoError
from modules.catalog.services.catalog_service import StockInsuficienteError
from modules.catalog.models.product import Product
from modules.catalog.models.stock import Stock
from modules.auth.models.user import User, UserRole
from modules.sales.schemas.sales_schema import CheckoutRequest, CartItemRequest

@pytest.fixture
def test_user(db_session):
    user = User(
        nombre="Test", 
        apellido="User", 
        email="sales_test@email.com", 
        password_hash="hash", 
        role=UserRole.CLIENTE
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def products(db_session):
    p1 = Product(nombre="Product 1", precio=100.0, activo=True)
    p2 = Product(nombre="Product 2", precio=50.0, activo=True)
    p3 = Product(nombre="Product Inactive", precio=20.0, activo=False)
    db_session.add_all([p1, p2, p3])
    db_session.commit()
    db_session.refresh(p1)
    db_session.refresh(p2)
    db_session.refresh(p3)
    
    s1 = Stock(product_id=p1.id, cantidad=10)
    s2 = Stock(product_id=p2.id, cantidad=5)
    db_session.add_all([s1, s2])
    db_session.commit()
    
    return {"p1": p1, "p2": p2, "p3": p3}

def test_checkout_success(db_session, test_user, products):
    service = SalesService(db_session)
    datos = CheckoutRequest(
        items=[
            CartItemRequest(product_id=products["p1"].id, cantidad=2),
            CartItemRequest(product_id=products["p2"].id, cantidad=1)
        ],
        direccion_entrega="Calle Falsa 123, Mar del Plata"
    )
    
    response = service.checkout(datos, test_user.id)
    
    assert response.orden_id is not None
    assert response.total == 250.0  # 100*2 + 50*1
    assert len(response.items) == 2
    assert response.items[0].producto_nombre == "Product 1"
    assert response.items[1].producto_nombre == "Product 2"
    
    # Verificar que el stock se descontó (vía OrderService)
    db_session.refresh(products["p1"].stock)
    db_session.refresh(products["p2"].stock)
    assert products["p1"].stock.cantidad == 8
    assert products["p2"].stock.cantidad == 4

def test_checkout_producto_invalido(db_session, test_user, products):
    service = SalesService(db_session)
    
    # Producto que no existe
    datos_inexistente = CheckoutRequest(
        items=[CartItemRequest(product_id=999, cantidad=1)],
        direccion_entrega="Calle Falsa 123, Mar del Plata"
    )
    with pytest.raises(ProductoInvalidoError):
        service.checkout(datos_inexistente, test_user.id)
        
    # Producto inactivo
    datos_inactivo = CheckoutRequest(
        items=[CartItemRequest(product_id=products["p3"].id, cantidad=1)],
        direccion_entrega="Calle Falsa 123, Mar del Plata"
    )
    with pytest.raises(ProductoInvalidoError):
        service.checkout(datos_inactivo, test_user.id)

def test_checkout_stock_insuficiente(db_session, test_user, products):
    service = SalesService(db_session)
    
    datos = CheckoutRequest(
        items=[CartItemRequest(product_id=products["p1"].id, cantidad=11)],
        direccion_entrega="Calle Falsa 123, Mar del Plata"
    )
    with pytest.raises(StockInsuficienteError):
        service.checkout(datos, test_user.id)
