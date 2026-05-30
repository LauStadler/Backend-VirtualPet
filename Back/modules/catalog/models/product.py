"""
Modelo de producto del catálogo.

Los productos son sincronizados desde el ERP externo directamente
en esta tabla. La API solo expone operaciones de lectura sobre ellos.

El campo 'activo' permite al ERP marcar productos como no disponibles
sin eliminarlos, preservando el historial de órdenes asociadas.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text, DateTime
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from infrastructure.db.base_class import Base


class Product(Base):
    """
    Tabla de productos del catálogo.

    Escrita exclusivamente por el ERP externo.
    Virtual Pet solo lee de esta tabla para mostrar el catálogo
    y validar disponibilidad durante el checkout.
    """

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)

    nombre = Column(String(200), nullable=False)
    """Nombre del producto tal como lo muestra el ERP. Ej: 'Alimento Royal Canin 15kg'."""

    descripcion = Column(Text, nullable=True)
    """Descripción larga del producto. Puede contener HTML básico."""

    precio = Column(Float, nullable=False)
    """
    Precio en pesos argentinos (ARS).
    El ERP es responsable de mantener este valor actualizado.
    """

    imagen_url = Column(String(500), nullable=True)
    """
    URL pública de la imagen del producto en AWS S3 + CloudFront.
    Null si el ERP aún no cargó imagen para este producto.
    """

    category_id = Column(Integer, sa.ForeignKey("categories.id"), nullable=True, index=True)
    """FK a la categoría (Mismo módulo)."""

    activo = Column(Boolean, default=True, nullable=False)
    """
    Si es False, el producto no aparece en el catálogo ni puede comprarse.
    El ERP lo usa para dar de baja productos sin eliminarlos.
    """

    erp_id = Column(String(100), unique=True, nullable=True)
    """
    Identificador del producto en el ERP externo.
    Permite al ERP sincronizar actualizaciones sin duplicar registros.
    """

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relaciones internas (Mismo módulo)
    category = relationship("Category", back_populates="products")
    stock = relationship("Stock", back_populates="product", uselist=False)

    def __repr__(self) -> str:
        return f"<Product id={self.id} nombre={self.nombre} precio={self.precio}>"
