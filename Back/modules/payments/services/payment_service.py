"""
Servicio de pagos.

Implementación simulada del procesamiento de pagos.
El pago siempre resulta aprobado — no hay integración con gateway externo.

Decisión de diseño — por qué existe este módulo si es simulado:
    Aislar la lógica de pago en su propio servicio permite que en el futuro
    se reemplace únicamente este archivo para integrar MercadoPago u otro
    gateway. El módulo de orders llama a PaymentService.procesar() sin
    saber ni importarle cómo se implementa el cobro por debajo.

Este servicio no expone endpoints HTTP. Es llamado internamente
por OrderService durante el flujo de checkout.
"""

from abc import ABC, abstractmethod
from sqlalchemy.orm import Session

from modules.payments.repositories.payment_repository import PaymentRepository
from modules.payments.models.payment import Payment, PaymentEstado


class IPaymentService(ABC):
    """Interfaz para el servicio de pagos."""

    @abstractmethod
    def procesar(self, orden_id: int, monto: float) -> Payment:
        pass


class PaymentService(IPaymentService):
    """Lógica de procesamiento de pagos. Actualmente simulado."""

    def __init__(self, db: Session) -> None:
        """
        Args:
            db: Sesión de base de datos inyectada por FastAPI.
        """
        self.repo = PaymentRepository(db)

    def procesar(self, orden_id: int, monto: float) -> Payment:
        """
        Procesa el pago de una orden y registra el resultado.

        Implementación actual: siempre aprueba el pago (simulado).

        Cuando se integre un gateway real, este método deberá:
          1. Llamar a la API del gateway con el monto.
          2. Recibir la respuesta (aprobado/rechazado/pendiente).
          3. Guardar la referencia_externa devuelta por el gateway.
          4. Lanzar PagoRechazadoError si el gateway rechaza el pago.

        Args:
            orden_id: ID de la orden a cobrar.
            monto: Monto total a cobrar en ARS.

        Returns:
            El objeto Payment registrado con estado 'aprobado'.
        """
        # TODO: reemplazar esta lógica por la llamada al gateway real
        # cuando se integre MercadoPago u otro proveedor.
        payment = self.repo.crear(
            orden_id=orden_id,
            monto=monto,
            estado=PaymentEstado.APROBADO,
            metodo="simulado",
        )
        return payment
