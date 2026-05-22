"""
Servicio del módulo sales.

Orquesta el flujo de checkout completo:
  1. Valida que los productos existen y están activos
  2. Verifica stock disponible para cada item
  3. Calcula el total con precios actualizados desde la DB
     (no confía en precios del frontend, que pueden estar desactualizados)
  4. Delega la creación de la orden al módulo de orders

Decisión de diseño — precios:
    El frontend mantiene el carrito con los precios que vio en el catálogo.
    Al hacer checkout, este servicio recalcula el total usando los precios
    actuales de la DB. Si el ERP actualizó un precio, el cliente paga el
    precio nuevo. Esto es el comportamiento estándar en ecommerce.

Decisión de diseño — stock:
    La verificación de stock ocurre en este servicio antes de crear la orden.
    El descuento efectivo ocurre en OrderService al confirmar.
    Si entre la verificación y el descuento otro cliente compró el mismo
    producto, OrderService lanzará StockInsuficienteError.
    Este caso borde es aceptable para el volumen esperado de Virtual Pet.
"""

from abc import ABC, abstractmethod
from sqlalchemy.orm import Session

from modules.catalog.repositories.catalog_repository import CatalogRepository
from modules.catalog.services.catalog_service import StockInsuficienteError
from modules.sales.schemas.sales_schema import (
    CheckoutRequest,
    CheckoutItemDetail,
    CheckoutResponse,
)


class ProductoInvalidoError(Exception):
    """
    Se lanza cuando un producto del carrito no existe o fue desactivado.
    Incluye el product_id para que el mensaje de error sea específico.
    """

    def __init__(self, product_id: int) -> None:
        self.product_id = product_id
        super().__init__(
            f"El producto {product_id} no está disponible. "
            "Es posible que haya sido removido del catálogo."
        )


class ISalesService(ABC):
    """Interfaz para el servicio del proceso de checkout."""

    @abstractmethod
    def checkout(self, datos: CheckoutRequest, user_id: int) -> CheckoutResponse:
        pass


class SalesService(ISalesService):
    """Lógica de negocio del proceso de checkout."""

    def __init__(self, db: Session) -> None:
        """
        Args:
            db: Sesión de base de datos inyectada por FastAPI.
        """
        self.db = db
        self.catalog_repo = CatalogRepository(db)

    def checkout(self, datos: CheckoutRequest, user_id: int) -> CheckoutResponse:
        """
        Ejecuta el flujo completo de checkout.

        Valida productos, verifica stock, calcula el total con precios
        actualizados y delega la creación de la orden a OrderService.

        Args:
            datos: Items del carrito y dirección de entrega enviados por el frontend.
            user_id: ID del usuario autenticado extraído del JWT.

        Returns:
            Detalle de la orden creada con precios confirmados por la API.

        Raises:
            ProductoInvalidoError: Si algún producto no existe o está inactivo.
            StockInsuficienteError: Si algún producto no tiene stock suficiente.
        """
        items_validados = self._validar_items(datos.items)
        total = sum(item.subtotal for item in items_validados)

        # Importación local para evitar circular imports entre módulos
        from modules.orders.services.order_service import OrderService
        order_service = OrderService(self.db)

        orden = order_service.crear_orden(
            user_id=user_id,
            items=items_validados,
            total=total,
            direccion_entrega=datos.direccion_entrega,
        )

        return CheckoutResponse(
            orden_id=orden.id,
            items=items_validados,
            total=total,
            direccion_entrega=datos.direccion_entrega,
        )

    def _validar_items(self, items: list) -> list[CheckoutItemDetail]:
        """
        Valida existencia, stock y calcula precios actualizados para cada item.

        Recorre todos los items antes de lanzar cualquier error para poder
        detectar múltiples problemas en una sola pasada. Esto evita que el
        cliente tenga que hacer checkout varias veces para descubrir todos
        los productos con problema.

        Args:
            items: Lista de CartItemRequest con product_id y cantidad.

        Returns:
            Lista de CheckoutItemDetail con precios confirmados desde la DB.

        Raises:
            ProductoInvalidoError: Al primer producto inválido encontrado.
            StockInsuficienteError: Al primer producto sin stock suficiente.
        """
        items_detallados = []

        for item in items:
            # Verificar que el producto existe y está activo
            product = self.catalog_repo.get_product_by_id(item.product_id)
            if product is None:
                raise ProductoInvalidoError(item.product_id)

            # Verificar stock suficiente para la cantidad pedida
            if not self.catalog_repo.hay_stock_suficiente(item.product_id, item.cantidad):
                stock = self.catalog_repo.get_stock(item.product_id)
                disponible = stock.cantidad if stock else 0
                raise StockInsuficienteError(
                    product_id=item.product_id,
                    disponible=disponible,
                    solicitado=item.cantidad,
                )

            # Usar precio actual de DB, no el del frontend
            precio_unitario = product.precio
            subtotal = round(precio_unitario * item.cantidad, 2)

            items_detallados.append(CheckoutItemDetail(
                product_id=product.id,
                producto_nombre=product.nombre,
                cantidad=item.cantidad,
                precio_unitario=precio_unitario,
                subtotal=subtotal,
            ))

        return items_detallados
