"""
Clase base declarativa de SQLAlchemy.

Separada de base.py para evitar circular imports.
Todos los modelos importan Base desde aquí.
base.py importa los modelos solo para que Alembic los detecte.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
