import pytest
from fastapi import status
from modules.catalog.models.category import Category
from modules.catalog.models.product import Product
from modules.catalog.models.stock import Stock

@pytest.fixture
def sample_catalog_data(db_session):
    # Crear categoría
    cat = Category(nombre="Alimentos", descripcion="Alimentos para mascotas")
    db_session.add(cat)
    db_session.commit()
    db_session.refresh(cat)
    
    # Crear producto con stock
    prod1 = Product(
        nombre="Royal Canin 15kg",
        precio=50000.0,
        category_id=cat.id,
        activo=True
    )
    db_session.add(prod1)
    db_session.commit()
    db_session.refresh(prod1)
    
    stock1 = Stock(product_id=prod1.id, cantidad=10)
    db_session.add(stock1)
    
    # Crear producto sin stock
    prod2 = Product(
        nombre="Juguete Hueso",
        precio=2000.0,
        category_id=cat.id,
        activo=True
    )
    db_session.add(prod2)
    db_session.commit()
    db_session.refresh(prod2)
    
    stock2 = Stock(product_id=prod2.id, cantidad=0)
    db_session.add(stock2)
    
    db_session.commit()
    return cat, prod1, prod2

def test_list_categories(client, sample_catalog_data):
    response = client.get("/catalog/categories")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1
    assert any(c["nombre"] == "Alimentos" for c in data)

def test_list_products_with_stock(client, sample_catalog_data):
    # Por defecto solo con stock
    response = client.get("/catalog/products")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    # Debería devolver solo Royal Canin (prod1)
    assert len(data["items"]) == 1
    assert data["items"][0]["nombre"] == "Royal Canin 15kg"

def test_list_products_all(client, sample_catalog_data):
    # Incluir sin stock
    response = client.get("/catalog/products?solo_con_stock=false")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["items"]) == 2

def test_get_product_detail(client, sample_catalog_data):
    _, prod1, _ = sample_catalog_data
    response = client.get(f"/catalog/products/{prod1.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["nombre"] == "Royal Canin 15kg"

def test_get_product_not_found(client):
    response = client.get("/catalog/products/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
