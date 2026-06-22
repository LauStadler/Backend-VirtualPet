"""merge billing and delivery heads

Revision ID: 31f16b8f7cd1
Revises: 16dbb3d5edd1, 8a9d4029e24a
Create Date: 2026-06-22 17:33:44.734936
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '31f16b8f7cd1'
down_revision: Union[str, None] = ('16dbb3d5edd1', '8a9d4029e24a')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
