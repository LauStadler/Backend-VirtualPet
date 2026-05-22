from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from shared.config.settings import settings
from shared.exceptions.handlers import register_exception_handlers

# Importar base.py registra todos los modelos en SQLAlchemy antes de que
# cualquier endpoint intente resolver relaciones entre tablas.
# Sin esto, relaciones como Order → Payment fallan con KeyError en runtime.
import infrastructure.db.base  # noqa: F401

from modules.auth.controllers.auth_controller import router as auth_router
from modules.catalog.controllers.product_controller import router as catalog_router
from modules.sales.controllers.cart_controller import router as sales_router
from modules.orders.controllers.order_controller import router as orders_router
from backoffice.controllers.backoffice_controller import router as backoffice_router

app = FastAPI(
    title="Virtual Pet API",
    description="Ecommerce de productos para mascotas - Mar del Plata",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(auth_router,       prefix="/auth",       tags=["Auth"])
app.include_router(catalog_router,    prefix="/catalog",    tags=["Catálogo"])
app.include_router(sales_router,      prefix="/cart",       tags=["Ventas"])
app.include_router(orders_router,     prefix="/orders",     tags=["Pedidos"])
app.include_router(backoffice_router, prefix="/backoffice", tags=["Backoffice"])

@app.get("/health")
def health_check():
    return {"status": "ok", "app": "Virtual Pet API"}
