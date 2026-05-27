"""
Modelo de item de una orden.

Representa cada producto dentro de una orden de compra.
Los precios se guardan como snapshot al momento de la compra:
si el ERP actualiza el precio de un producto después, el historial
de órdenes no se ve afectado.
"""

from sqlalchemy import Column, Integer, Float, ForeignKey, String
from sqlalchemy.orm import relationship
from infrastructure.db.base_class import Base


class OrderItem(Base):
    """
    Tabla de items de órdenes.

    Relación muchos-a-uno con Order.
    Cada fila representa un producto y cantidad dentro de una orden.
    """

    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, autoincrement=True)

    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    """FK a la orden a la que pertenece este item."""

    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    """FK al producto comprado. Se mantiene para referencias futuras."""

    cantidad = Column(Integer, nullable=False)
    """Unidades compradas de este producto."""

    precio_unitario = Column(Float, nullable=False)
    """
    Precio unitario al momento de la compra (snapshot).
    Independiente del precio actual del producto en el catálogo.
    Garantiza que el historial de órdenes sea inmutable.
    """

    producto_nombre = Column(String(200), nullable=True)
    """Nombre del producto al momento de la compra."""

    subtotal = Column(Float, nullable=False)
    """precio_unitario × cantidad. Calculado al crear la orden."""

    # Relaciones
    order = relationship("Order", back_populates="items")
    product = relationship("Product")

    @property
    def producto_imagen_url(self) -> str:
        """Retorna la URL de la imagen del producto asociado."""
        return self.product.imagen_url if self.product else None

    def __repr__(self) -> str:
        return (
            f"<OrderItem id={self.id} order_id={self.order_id} "
            f"product_id={self.product_id} cantidad={self.cantidad}>"
        )
