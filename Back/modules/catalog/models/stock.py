"""
Modelo de stock de productos.

Tabla separada de products por diseño deliberado: permite que el ERP
actualice cantidades de stock de forma independiente a los datos del producto,
y facilita agregar lógica de stock en el futuro sin modificar la tabla principal.

El stock se descuenta únicamente al confirmar una compra.
No existe reserva por carrito — el orden de compra determina quién se queda
con las últimas unidades disponibles.
"""

from sqlalchemy import Column, Integer, ForeignKey, DateTime
import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from infrastructure.db.base_class import Base


class Stock(Base):
    """
    Tabla de stock disponible por producto.

    Relación uno-a-uno con Product.
    El ERP escribe la cantidad inicial y la actualiza con reposiciones.
    El sistema de Virtual Pet descuenta al confirmar cada compra.
    """

    __tablename__ = "stock"

    id = Column(Integer, primary_key=True, autoincrement=True)

    product_id = Column(
        Integer,
        sa.ForeignKey("products.id"),
        unique=True,
        nullable=False
    )
    """FK al producto (Mismo módulo)."""

    cantidad = Column(Integer, nullable=False, default=0)
    """
    Unidades disponibles para la venta.
    Se descuenta en el momento de confirmar la compra, no al agregar al carrito.
    No puede ser negativo — el sistema verifica disponibilidad antes de descontar.
    """

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    """
    Última vez que se modificó el stock.
    Útil para auditar cuándo el ERP repuso mercadería o cuándo se realizó una venta.
    """

    # Relaciones internas (Mismo módulo)
    product = relationship("Product", back_populates="stock")

    def __repr__(self) -> str:
        return f"<Stock product_id={self.product_id} cantidad={self.cantidad}>"
