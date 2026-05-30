"""remove_remaining_fks

Revision ID: 5a12f04539db
Revises: 4fb4bc3f8b80
Create Date: 2026-05-30

"""
from typing import Sequence, Optional

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5a12f04539db'
down_revision: Optional[str] = '4fb4bc3f8b80'
branch_labels: Optional[Sequence[str]] = None
depends_on: Optional[Sequence[str]] = None


def upgrade() -> None:
    # 1. Eliminar FKs restantes identificadas en MySQL:
    # order_items: order_items_ibfk_1 (order_id -> orders.id)
    # products: products_ibfk_1 (category_id -> categories.id)
    # stock: stock_ibfk_1 (product_id -> products.id)
    # categories: categories_ibfk_1 (parent_id -> categories.id)
    
    op.drop_constraint('order_items_ibfk_1', 'order_items', type_='foreignkey')
    op.drop_constraint('products_ibfk_1', 'products', type_='foreignkey')
    op.drop_constraint('stock_ibfk_1', 'stock', type_='foreignkey')
    op.drop_constraint('categories_ibfk_1', 'categories', type_='foreignkey')


def downgrade() -> None:
    # Restaurar FKs
    op.create_foreign_key('order_items_ibfk_1', 'order_items', 'orders', ['order_id'], ['id'])
    op.create_foreign_key('products_ibfk_1', 'products', 'categories', ['category_id'], ['id'])
    op.create_foreign_key('stock_ibfk_1', 'stock', 'products', ['product_id'], ['id'])
    op.create_foreign_key('categories_ibfk_1', 'categories', 'categories', ['parent_id'], ['id'])
