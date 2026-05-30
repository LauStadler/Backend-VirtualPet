"""
Servicio de órdenes.

Es el punto de coordinación central del checkout:
  1. Crea la orden con sus items
  2. Descuenta el stock de cada producto via CatalogService
  3. Registra el pago via PaymentService

También gestiona el ciclo de vida de la orden:
  - Consultas del cliente (sus propias órdenes)
  - Cambios de estado desde el backoffice

Regla crítica de negocio — transiciones de estado:
    Los estados solo avanzan en la dirección definida en TRANSICIONES_VALIDAS.
    El backoffice no puede retroceder un estado ni saltearse pasos.
    Esto garantiza consistencia en el seguimiento de pedidos.

Regla crítica de negocio — atomicidad del checkout:
    La creación de la orden, el descuento de stock y el registro del pago
    ocurren dentro de la misma sesión de SQLAlchemy. Si cualquier paso
    falla, la sesión se revierte y no queda ningún dato a medias.
"""

from abc import ABC, abstractmethod
from sqlalchemy.orm import Session

from modules.catalog.models.product import Product
from modules.orders.repositories.order_repository import OrderRepository
from modules.orders.models.order import Order, OrderEstado, TRANSICIONES_VALIDAS
from modules.orders.schemas.order_schema import (
    OrderResponse,
    OrderSummaryResponse,
    BackofficeOrderResponse,
)
from modules.sales.schemas.sales_schema import CheckoutItemDetail
from modules.catalog.services.catalog_service import CatalogService, StockInsuficienteError


class OrdenNoEncontradaError(Exception):
    """Se lanza cuando se consulta una orden que no existe o no pertenece al usuario."""
    pass


class TransicionEstadoInvalidaError(Exception):
    """
    Se lanza cuando el backoffice intenta un cambio de estado no permitido.
    Incluye el estado actual y el estado solicitado para un mensaje claro.
    """

    def __init__(self, estado_actual: OrderEstado, estado_solicitado: OrderEstado) -> None:
        self.estado_actual = estado_actual
        self.estado_solicitado = estado_solicitado
        siguientes = TRANSICIONES_VALIDAS.get(estado_actual, [])
        siguientes_str = ", ".join([s.value for s in siguientes]) if siguientes else "ninguno (estado final)"
        super().__init__(
            f"No se puede cambiar de '{estado_actual.value}' a '{estado_solicitado.value}'. "
            f"Los siguientes estados válidos desde '{estado_actual.value}' son: {siguientes_str}."
        )


class IOrderService(ABC):
    """Interfaz para el servicio de órdenes."""

    @abstractmethod
    def crear_orden(
        self,
        user_id: int,
        items: list[CheckoutItemDetail],
        total: float,
        direccion_entrega: str,
    ) -> Order:
        pass

    @abstractmethod
    def listar_mis_ordenes(self, user_id: int) -> list[OrderSummaryResponse]:
        pass

    @abstractmethod
    def obtener_mi_orden(self, order_id: int, user_id: int) -> OrderResponse:
        pass

    @abstractmethod
    def listar_todas(self) -> list[BackofficeOrderResponse]:
        pass

    @abstractmethod
    def obtener_una_backoffice(self, order_id: int) -> BackofficeOrderResponse:
        pass

    @abstractmethod
    def cambiar_estado(self, order_id: int, nuevo_estado: OrderEstado) -> BackofficeOrderResponse:
        pass


class OrderService(IOrderService):
    """Lógica de negocio para creación y gestión del ciclo de vida de órdenes."""

    def __init__(self, db: Session) -> None:
        """
        Args:
            db: Sesión de base de datos inyectada por FastAPI.
        """
        self.db = db
        self.repo = OrderRepository(db)

    def crear_orden(
        self,
        user_id: int,
        items: list[CheckoutItemDetail],
        total: float,
        direccion_entrega: str,
    ) -> Order:
        """
        Crea una orden, descuenta stock y registra el pago en una sola operación atómica.

        Este método es el único responsable de realizar el commit() final.
        Si cualquier paso falla, se realiza un rollback() para mantener la integridad.
        """
        try:
            # 1. Validar productos y RECALCULAR precios desde la DB para evitar inyecciones
            total_real = 0.0
            for item in items:
                product = self.db.query(Product).filter(Product.id == item.product_id).first()
                if not product:
                    raise Exception(f"Producto {item.product_id} no encontrado")
                
                # Forzamos los valores reales de la DB
                item.precio_unitario = float(product.precio)
                item.subtotal = float(product.precio * item.cantidad)
                total_real += item.subtotal

            # 2. Crear la orden y sus items con los datos ya validados
            # Inyectamos el producto_imagen_url para que quede persistido en la orden
            for item in items:
                product = self.db.query(Product).filter(Product.id == item.product_id).first()
                if product:
                    item.producto_imagen_url = product.imagen_url

            order = self.repo.crear(
                user_id=user_id,
                items=items,
                total=float(total_real),
                direccion_entrega=direccion_entrega,
            )

            # 3. Descontar stock de cada item con bloqueo pesimista
            catalog_service = CatalogService(self.db)
            for item in items:
                # El método descontar_stock ahora usa with_for_update() internamente
                catalog_service.descontar_stock(item.product_id, item.cantidad)

            # 4. Registrar el pago simulado
            from modules.payments.services.payment_service import PaymentService
            PaymentService(self.db).procesar(orden_id=order.id, monto=float(total_real))

            # Commit final de toda la unidad de trabajo
            self.db.commit()
            self.db.refresh(order)
            return order

        except Exception as e:
            self.db.rollback()
            raise e

    def listar_mis_ordenes(self, user_id: int) -> list[OrderSummaryResponse]:
        """
        Retorna el historial de compras del usuario autenticado.

        Args:
            user_id: ID del usuario extraído del JWT.

        Returns:
            Lista de órdenes del usuario, la más reciente primero.
        """
        orders = self.repo.list_by_user(user_id)
        return [OrderSummaryResponse.model_validate(o) for o in orders]

    def obtener_mi_orden(self, order_id: int, user_id: int) -> OrderResponse:
        """
        Retorna el detalle de una orden verificando que pertenezca al usuario.

        Args:
            order_id: ID de la orden a consultar.
            user_id: ID del usuario autenticado (del JWT).

        Returns:
            Detalle completo de la orden con sus items.

        Raises:
            OrdenNoEncontradaError: Si la orden no existe o no pertenece al usuario.
        """
        order = self.repo.get_by_id_and_user(order_id, user_id)
        if order is None:
            raise OrdenNoEncontradaError(
                f"La orden {order_id} no existe o no te pertenece."
            )
        return OrderResponse.model_validate(order)

    def listar_todas(self) -> list[BackofficeOrderResponse]:
        """
        Retorna todas las órdenes del sistema para el backoffice.
        Solo debe ser llamado desde endpoints con rol DEPOSITO o ADMIN.

        Returns:
            Lista de todas las órdenes con datos del cliente, la más reciente primero.
        """
        from modules.auth.repositories.user_repository import UserRepository
        user_repo = UserRepository(self.db)
        
        orders = self.repo.list_all()
        
        # Hidratación manual de usuarios (Búsqueda por lote)
        user_ids = list(set(o.user_id for o in orders))
        users = user_repo.get_by_ids(user_ids)
        user_map = {u.id: u for u in users}

        responses = []
        for o in orders:
            resp = BackofficeOrderResponse.model_validate(o)
            # Asignamos el usuario si existe, manejando resiliencia si no se encuentra
            resp.user = user_map.get(o.user_id)
            responses.append(resp)
            
        return responses

    def obtener_una_backoffice(self, order_id: int) -> BackofficeOrderResponse:
        """
        Retorna el detalle de una orden con el formato extendido para backoffice.
        """
        from modules.auth.repositories.user_repository import UserRepository
        user_repo = UserRepository(self.db)

        order = self.repo.get_by_id(order_id)
        if order is None:
            raise OrdenNoEncontradaError(f"La orden {order_id} no existe.")
        
        resp = BackofficeOrderResponse.model_validate(order)
        resp.user = user_repo.get_by_id(order.user_id)
        
        return resp

    def cambiar_estado(self, order_id: int, nuevo_estado: OrderEstado) -> BackofficeOrderResponse:
        """
        Avanza el estado de una orden al siguiente estado válido.

        Solo el backoffice puede llamar a este método.
        La validación garantiza que los estados siempre avanzan en orden
        y nunca retroceden ni se saltean pasos.

        Args:
            order_id: ID de la orden a actualizar.
            nuevo_estado: Estado al que se quiere avanzar.

        Returns:
            La orden actualizada con el nuevo estado.

        Raises:
            OrdenNoEncontradaError: Si la orden no existe.
            TransicionEstadoInvalidaError: Si el cambio de estado no está permitido.
        """
        order = self.repo.get_by_id(order_id)
        if order is None:
            raise OrdenNoEncontradaError(f"La orden {order_id} no existe.")

        estado_actual = OrderEstado(order.estado)
        transiciones_permitidas = TRANSICIONES_VALIDAS.get(estado_actual, [])

        # Verificar que la transición solicitada está permitida para el estado actual
        if nuevo_estado not in transiciones_permitidas:
            print(f"DEBUG: Transition conflict for order {order_id}. Actual: {estado_actual}, Requested: {nuevo_estado}, Valid: {transiciones_permitidas}")
            raise TransicionEstadoInvalidaError(estado_actual, nuevo_estado)

        if nuevo_estado == OrderEstado.CANCELADO:
            # Si se cancela, devolvemos el stock al catálogo
            catalog_service = CatalogService(self.db)
            for item in order.items:
                # El método sumar_stock debería existir o ser creado para devolver stock
                catalog_service.sumar_stock(item.product_id, item.cantidad)

        order = self.repo.actualizar_estado(order, nuevo_estado)
        self.db.commit()
        self.db.refresh(order)
        
        # Hidratación manual del usuario para la respuesta del backoffice
        from modules.auth.repositories.user_repository import UserRepository
        user_repo = UserRepository(self.db)
        
        resp = BackofficeOrderResponse.model_validate(order)
        resp.user = user_repo.get_by_id(order.user_id)
        
        return resp
