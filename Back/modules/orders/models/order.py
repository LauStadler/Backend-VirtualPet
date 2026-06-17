"""
Modelo de orden de compra.

Una orden se crea al confirmar el checkout y representa
el compromiso de entrega de Virtual Pet al cliente.

El campo 'estado' refleja en qué etapa del proceso está la orden.
Los cambios de estado los realiza el equipo de depósito via backoffice.
La trazabilidad detallada (historial de cambios con fechas) es una
mejora planificada para una versión futura.
"""

from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from infrastructure.db.base_class import Base
import enum


class OrderEstado(str, enum.Enum):
    """
    Estados del ciclo de vida de una orden.
    """
    PENDIENTE = "pendiente"
    PREPARADO = "preparado"
    EN_PREPARACION = "en_preparacion"
    DESPACHADO = "despachado"
    ENTREGADO = "entregado"
    CANCELADO = "cancelado"

# Define el orden válido de transiciones de estado.
TRANSICIONES_VALIDAS: dict[OrderEstado, list[OrderEstado]] = {
    OrderEstado.PENDIENTE: [OrderEstado.EN_PREPARACION, OrderEstado.CANCELADO],
    OrderEstado.EN_PREPARACION: [OrderEstado.PENDIENTE, OrderEstado.PREPARADO, OrderEstado.CANCELADO],
    OrderEstado.PREPARADO: [OrderEstado.DESPACHADO, OrderEstado.EN_PREPARACION, OrderEstado.CANCELADO],
    OrderEstado.DESPACHADO: [OrderEstado.PREPARADO, OrderEstado.ENTREGADO, OrderEstado.CANCELADO],
    OrderEstado.ENTREGADO: [OrderEstado.DESPACHADO],
    OrderEstado.CANCELADO: [], # Estado final
}
"""
Mapa de transiciones válidas de estado.
Permite avanzar y retroceder entre estados contiguos para corregir errores manuales.
"""


class Order(Base):
    """
    Tabla de órdenes de compra.

    Cada orden pertenece a un usuario y tiene uno o más items.
    El pago asociado se registra en la tabla 'payments'.
    """

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(Integer, nullable=False, index=True)
    """ID del usuario que realizó la compra (Referencia lógica)."""

    estado = Column(
        String(20),
        nullable=False,
        default=OrderEstado.PENDIENTE,
    )
    """Estado actual de la orden. Ver OrderEstado para el flujo completo."""

    total = Column(Float, nullable=False)
    """Total cobrado en ARS. Calculado al momento del checkout."""

    direccion_entrega = Column(String(300), nullable=False)
    """Dirección de entrega ingresada por el cliente al hacer checkout."""

    billing_cuit = Column(String(11), nullable=True)
    """CUIT para facturación, solicitado via chatbot."""

    billing_requested_at = Column(DateTime, nullable=True)
    """Fecha en la que se solicitó la facturación."""

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relaciones
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Order id={self.id} user_id={self.user_id} estado={self.estado} total={self.total}>"
