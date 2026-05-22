"""
Modelo de pago.

Registra el historial de pagos asociados a órdenes de compra.
En la implementación actual el pago es simulado y siempre se aprueba.

Separar esta tabla de 'orders' tiene valor a futuro: cuando se integre
un gateway real (MercadoPago, Stripe), esta tabla almacenará el ID de
transacción externo, el medio de pago, y otros datos sin necesidad de
modificar la tabla de órdenes.
"""

from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from infrastructure.db.base_class import Base
import enum


class PaymentEstado(str, enum.Enum):
    """
    Estados posibles de un pago.

    En la implementación simulada solo se usa APROBADO.
    RECHAZADO y PENDIENTE están definidos para cuando se integre
    un gateway real sin necesidad de modificar el modelo.
    """
    APROBADO = "aprobado"
    RECHAZADO = "rechazado"
    PENDIENTE = "pendiente"


class Payment(Base):
    """
    Tabla de pagos.

    Un pago está siempre asociado a una orden. En el flujo actual,
    el pago se crea simultáneamente con la orden y siempre resulta aprobado.
    """

    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, autoincrement=True)

    orden_id = Column(
        Integer,
        ForeignKey("orders.id"),
        nullable=False,
        unique=True,
    )
    """
    FK a la orden asociada. Unique porque una orden tiene exactamente un pago.
    """

    monto = Column(Float, nullable=False)
    """Monto total cobrado en pesos argentinos (ARS)."""

    estado = Column(
        String(20),
        nullable=False,
        default=PaymentEstado.APROBADO,
    )
    """
    Estado del pago. Actualmente siempre 'aprobado' (simulado).
    Cuando se integre un gateway real, puede ser 'rechazado' o 'pendiente'.
    """

    metodo = Column(String(50), nullable=False, default="simulado")
    """
    Método de pago utilizado. 
    Valor actual: 'simulado'.
    A futuro: 'mercadopago', 'tarjeta', 'transferencia', etc.
    """

    referencia_externa = Column(String(200), nullable=True)
    """
    ID de transacción del gateway externo.
    Null en la implementación simulada.
    A futuro: ID de MercadoPago para rastrear el pago en su plataforma.
    """

    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relaciones
    orden = relationship("Order", back_populates="payment")

    def __repr__(self) -> str:
        return f"<Payment id={self.id} orden_id={self.orden_id} estado={self.estado} monto={self.monto}>"
