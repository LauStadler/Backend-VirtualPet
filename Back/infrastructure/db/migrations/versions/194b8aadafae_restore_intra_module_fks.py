"""restore_intra_module_fks

Revision ID: 194b8aadafae
Revises: 5a12f04539db
Create Date: 2026-05-30
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '194b8aadafae'
down_revision: Union[str, None] = '5a12f04539db'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Restaurar Foreign Keys internas (mismo módulo)
    op.create_foreign_key('order_items_ibfk_1', 'order_items', 'orders', ['order_id'], ['id'])
    op.create_foreign_key('products_ibfk_1', 'products', 'categories', ['category_id'], ['id'])
    op.create_foreign_key('stock_ibfk_1', 'stock', 'products', ['product_id'], ['id'])
    op.create_foreign_key('categories_ibfk_1', 'categories', 'categories', ['parent_id'], ['id'])


def downgrade() -> None:
    # Eliminar Foreign Keys internas
    op.drop_constraint('order_items_ibfk_1', 'order_items', type_='foreignkey')
    op.drop_constraint('products_ibfk_1', 'products', type_='foreignkey')
    op.drop_constraint('stock_ibfk_1', 'stock', type_='foreignkey')
    op.drop_constraint('categories_ibfk_1', 'categories', type_='foreignkey')
