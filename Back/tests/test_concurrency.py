import os
import pytest
import concurrent.futures
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from infrastructure.db.base import Base
from modules.orders.services.order_service import OrderService
from modules.catalog.services.catalog_service import StockInsuficienteError
from modules.sales.schemas.sales_schema import CheckoutItemDetail

# Usamos un archivo físico temporal para evitar los problemas de StaticPool en memoria
DB_FILE = "test_concurrency.db"
engine_shared = create_engine(
    f"sqlite:///{DB_FILE}",
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(bind=engine_shared)

@pytest.fixture(autouse=True)
def setup_teardown_db():
    # Setup: Crear tablas
    Base.metadata.drop_all(engine_shared)
    Base.metadata.create_all(engine_shared)
    yield
    # Teardown: Limpiar archivo
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

def test_concurrencia_descuento_stock(db_session):
    """
    Test de concurrencia: Dos hilos intentan comprar el último producto disponible.
    """
    # 1. Setup: Insertar un producto con stock 1 en la base del archivo
    from modules.catalog.models.product import Product
    from modules.catalog.models.stock import Stock
    
    # Usamos una sesión fresca del engine compartido
    setup_session = TestingSessionLocal()
    product = Product(nombre="Prod Concurrente", precio=10.0, activo=True)
    setup_session.add(product)
    setup_session.commit()
    
    stock = Stock(product_id=product.id, cantidad=1)
    setup_session.add(stock)
    setup_session.commit()
    product_id = product.id
    setup_session.close()

    # 2. Definir acción de compra
    def intentar_compra():
        thread_session = TestingSessionLocal()
        try:
            service = OrderService(thread_session)
            item = CheckoutItemDetail(
                product_id=product_id, 
                cantidad=1, 
                precio_unitario=10.0, 
                subtotal=10.0, 
                producto_nombre="Prod Concurrente"
            )
            # Intentamos crear la orden
            return service.crear_orden(user_id=1, items=[item], total=10.0, direccion_entrega="Calle Falsa 123")
        except Exception as e:
            return e
        finally:
            thread_session.close()

    # 3. Ejecutar concurrentemente
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(intentar_compra) for _ in range(2)]
        resultados = [f.result() for f in futures]
    
    # 4. Validar
    exitos = [r for r in resultados if not isinstance(r, Exception)]
    errores = [r for r in resultados if isinstance(r, Exception)]
    
    # Log para ver qué falló si no sale bien
    if len(exitos) != 1:
        for i, r in enumerate(resultados):
            if isinstance(r, Exception):
                print(f"Hilo {i} falló con: {type(r).__name__}: {r}")

    assert len(exitos) == 1, f"Debería haber solo 1 éxito, pero hubo {len(exitos)}"
    assert len(errores) == 1, f"Debería haber 1 error de stock, pero hubo {len(errores)}"
    assert any(isinstance(e, StockInsuficienteError) for e in errores), "El error debería ser StockInsuficienteError"
