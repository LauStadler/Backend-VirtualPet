import pytest
from modules.catalog.services.catalog_service import CatalogService, StockInsuficienteError
from modules.catalog.models.product import Product
from modules.catalog.models.stock import Stock

@pytest.fixture
def product_with_stock(db_session):
    prod = Product(nombre="Test Product", precio=10.0, activo=True)
    db_session.add(prod)
    db_session.commit()
    db_session.refresh(prod)
    
    stock = Stock(product_id=prod.id, cantidad=5)
    db_session.add(stock)
    db_session.commit()
    return prod

def test_descontar_stock_success(db_session, product_with_stock):
    service = CatalogService(db_session)
    service.descontar_stock(product_with_stock.id, 3)
    
    db_session.refresh(product_with_stock.stock)
    assert product_with_stock.stock.cantidad == 2

def test_descontar_stock_insufficient(db_session, product_with_stock):
    service = CatalogService(db_session)
    with pytest.raises(StockInsuficienteError):
        service.descontar_stock(product_with_stock.id, 10)
