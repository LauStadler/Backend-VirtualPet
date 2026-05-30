"""
Modelo de categoría de productos.

Las categorías son creadas y mantenidas por el ERP externo.
La API de Virtual Pet solo las lee para mostrarlas en el catálogo
y permitir filtrado por categoría.

Ejemplos de categorías: Alimentos, Juguetes, Accesorios, Higiene, Cuchas.
"""

from sqlalchemy import Column, Integer, String, ForeignKey
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from infrastructure.db.base_class import Base


class Category(Base):
    """
    Tabla de categorías de productos.

    Soporta jerarquía de un nivel: una categoría puede tener
    una categoría padre (ej: "Alimentos para perros" → padre: "Alimentos").
    El ERP es el único que escribe en esta tabla.
    """

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)

    nombre = Column(String(100), nullable=False, unique=True)
    """Nombre visible de la categoría. Ej: 'Alimentos para perros'."""

    descripcion = Column(String(255), nullable=True)
    """Descripción opcional de la categoría."""

    parent_id = Column(Integer, sa.ForeignKey("categories.id"), nullable=True, index=True)
    """
    ID de la categoría padre (FK interna). Null si es categoría raíz.
    Permite una jerarquía simple de dos niveles (padre → hijo).
    """

    # Relaciones internas (Mismo módulo)
    parent = relationship("Category", remote_side=[id], back_populates="children")
    children = relationship("Category", back_populates="parent")
    products = relationship("Product", back_populates="category")

    def __repr__(self) -> str:
        return f"<Category id={self.id} nombre={self.nombre}>"
