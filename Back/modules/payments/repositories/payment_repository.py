"""
Repositorio de pagos.

Centraliza las queries a la tabla 'payments'.
Al ser un módulo de registro interno, las operaciones
son simples: crear y consultar pagos.
"""

from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional

from modules.payments.models.payment import Payment, PaymentEstado


class PaymentRepository:
    """Acceso a datos para la entidad Payment."""

    def __init__(self, db: Session) -> None:
        """
        Args:
            db: Sesión activa de SQLAlchemy inyectada por FastAPI.
        """
        self.db = db

    def crear(self, orden_id: int, monto: float, estado: PaymentEstado, metodo: str) -> Payment:
        """
        Persiste un nuevo registro de pago en la base de datos.

        IMPORTANTE: Ya no hace commit(). La transacción debe ser gestionada
        externamente (ej: en OrderService).

        Args:
            orden_id: ID de la orden a la que pertenece el pago.
            monto: Monto total cobrado.
            estado: Estado del pago (aprobado/rechazado/pendiente).
            metodo: Método de pago utilizado (ej: 'simulado').

        Returns:
            El objeto Payment recién creado.
        """
        payment = Payment(
            orden_id=orden_id,
            monto=monto,
            estado=estado,
            metodo=metodo,
        )
        self.db.add(payment)
        self.db.flush()
        return payment

    def get_by_orden_id(self, orden_id: int) -> Optional[Payment]:
        """
        Busca el pago asociado a una orden específica.

        Args:
            orden_id: ID de la orden a consultar.

        Returns:
            El Payment si existe, None si la orden no tiene pago registrado.
        """
        stmt = select(Payment).where(Payment.orden_id == orden_id)
        return self.db.scalar(stmt)
