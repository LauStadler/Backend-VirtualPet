"""
Punto de registro de todos los modelos para Alembic.

Este archivo NO debe ser importado por los modelos — solo por Alembic
y por el env.py de migraciones. Los modelos importan Base desde base_class.py.

Al importar todos los modelos aquí, Alembic los detecta automáticamente
al generar migraciones con: alembic revision --autogenerate
"""

from infrastructure.db.base_class import Base  # noqa: F401 — necesario para Alembic

# Importar todos los modelos para que queden registrados en Base.metadata
from modules.auth.models.user import User  # noqa: F401
from modules.catalog.models.category import Category  # noqa: F401
from modules.catalog.models.product import Product  # noqa: F401
from modules.catalog.models.stock import Stock  # noqa: F401
from modules.payments.models.payment import Payment  # noqa: F401
from modules.orders.models.order import Order  # noqa: F401
from modules.orders.models.order_item import OrderItem  # noqa: F401
