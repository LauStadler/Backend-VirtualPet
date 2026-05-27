"""add_fulltext_index_to_products

Revision ID: ebc4ab637536
Revises: e4e858e5f6cf
Create Date: 2026-05-27 15:46:25.873710
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'ebc4ab637536'
down_revision: Union[str, None] = 'e4e858e5f6cf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Añadimos el índice FULLTEXT a las columnas nombre y descripcion
    # Usamos execute directo porque el soporte nativo de FULLTEXT en op.create_index varía según el dialecto
    op.execute("ALTER TABLE products ADD FULLTEXT INDEX idx_products_fulltext (nombre, descripcion)")


def downgrade() -> None:
    # Eliminamos el índice
    op.execute("ALTER TABLE products DROP INDEX idx_products_fulltext")
