"""decouple_fks_and_add_product_image

Revision ID: 4fb4bc3f8b80
Revises: ebc4ab637536
Create Date: 2026-05-30

"""
from typing import Sequence, Optional

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4fb4bc3f8b80'
down_revision: Optional[str] = 'ebc4ab637536'
branch_labels: Optional[Sequence[str]] = None
depends_on: Optional[Sequence[str]] = None


def upgrade() -> None:
    # 1. Eliminar Foreign Keys
    # Los nombres de los constraints identificados en MySQL son:
    # orders: orders_ibfk_1 (user_id -> users.id)
    # order_items: order_items_ibfk_2 (product_id -> products.id)
    # payments: payments_ibfk_1 (orden_id -> orders.id)
    
    op.drop_constraint('orders_ibfk_1', 'orders', type_='foreignkey')
    op.drop_constraint('order_items_ibfk_2', 'order_items', type_='foreignkey')
    op.drop_constraint('payments_ibfk_1', 'payments', type_='foreignkey')

    # 2. Agregar columna producto_imagen_url a order_items
    op.add_column('order_items', sa.Column('producto_imagen_url', sa.String(length=500), nullable=True))

    # 3. Migración de Datos: Poblar producto_imagen_url con la URL actual de la tabla products
    # Usamos SQL directo para eficiencia
    op.execute(
        "UPDATE order_items oi "
        "INNER JOIN products p ON oi.product_id = p.id "
        "SET oi.producto_imagen_url = p.imagen_url"
    )

    # 4. Asegurar índices (SQLAlchemy los creará si no existen)
    # user_id en orders ya tiene KEY `user_id`, product_id en order_items ya tiene KEY `product_id`
    pass


def downgrade() -> None:
    # 1. Eliminar columna producto_imagen_url
    op.drop_column('order_items', 'producto_imagen_url')

    # 2. Restaurar Foreign Keys
    op.create_foreign_key('orders_ibfk_1', 'orders', 'users', ['user_id'], ['id'])
    op.create_foreign_key('order_items_ibfk_2', 'order_items', 'products', ['product_id'], ['id'])
    op.create_foreign_key('payments_ibfk_1', 'payments', 'orders', ['orden_id'], ['id'])
