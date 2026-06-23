"""fix_user_roles_casing

Revision ID: 986ecc512068
Revises: e7aa98997eb5
Create Date: 2026-06-22 21:56:32.023753
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '986ecc512068'
down_revision: Union[str, None] = 'e7aa98997eb5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Convertir roles antiguos en mayúsculas a minúsculas para que coincidan con UserRole
    op.execute("UPDATE users SET role = 'cliente' WHERE role = 'CLIENTE'")
    op.execute("UPDATE users SET role = 'deposito' WHERE role = 'DEPOSITO'")
    op.execute("UPDATE users SET role = 'delivery' WHERE role = 'DELIVERY'")
    op.execute("UPDATE users SET role = 'admin' WHERE role = 'ADMIN'")


def downgrade() -> None:
    pass
