"""
Servicio del catálogo de productos.

Orquesta la lógica de negocio relacionada al catálogo.
Al ser un módulo de solo lectura, la mayoría de la lógica
es delegación al repositorio con cálculos de paginación.

La operación descontar_stock() es la única que modifica datos
y es llamada exclusivamente por el módulo de orders — nunca
por un endpoint HTTP del catálogo.
"""

import math
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from typing import Optional

from modules.catalog.repositories.catalog_repository import CatalogRepository
from modules.catalog.schemas.catalog_schema import (
    ProductFilterParams,
    ProductListResponse,
    ProductDetailResponse,
    ProductSummaryResponse,
    CategoryResponse,
)
from modules.catalog.models.product import Product


class ProductoNoEncontradoError(Exception):
    """Se lanza cuando se solicita un producto que no existe o está inactivo."""
    pass


class StockInsuficienteError(Exception):
    """
    Se lanza cuando se intenta descontar más stock del disponible.
    Incluye el product_id para que el módulo de orders pueda identificar
    cuál producto causó el problema al procesar órdenes con múltiples items.
    """

    def __init__(self, product_id: int, disponible: int, solicitado: int) -> None:
        self.product_id = product_id
        self.disponible = disponible
        self.solicitado = solicitado
        super().__init__(
            f"Stock insuficiente para el producto {product_id}: "
            f"disponible={disponible}, solicitado={solicitado}"
        )


class ICatalogService(ABC):
    """Interfaz para el servicio del catálogo de productos."""

    @abstractmethod
    def listar_productos(self, filtros: ProductFilterParams) -> ProductListResponse:
        pass

    @abstractmethod
    def obtener_producto(self, product_id: int) -> ProductDetailResponse:
        pass

    @abstractmethod
    def listar_categorias(self) -> list[CategoryResponse]:
        pass

    @abstractmethod
    def verificar_stock(self, product_id: int, cantidad: int) -> bool:
        pass

    @abstractmethod
    def descontar_stock(self, product_id: int, cantidad: int) -> None:
        pass


class CatalogService(ICatalogService):
    """Lógica de negocio del catálogo de productos."""

    def __init__(self, db: Session) -> None:
        """
        Args:
            db: Sesión de base de datos inyectada por FastAPI.
        """
        self.repo = CatalogRepository(db)

    def listar_productos(self, filtros: ProductFilterParams) -> ProductListResponse:
        """
        Lista productos activos aplicando filtros y paginación.

        Calcula los metadatos de paginación (total_pages) para que el
        frontend pueda implementar navegación sin hacer consultas adicionales.

        Args:
            filtros: Parámetros de búsqueda, filtrado y paginación.

        Returns:
            Lista paginada de productos con metadatos de paginación.
        """
        products, total = self.repo.list_products(
            busqueda=filtros.busqueda,
            categoria_id=filtros.categoria_id,
            solo_con_stock=filtros.solo_con_stock,
            page=filtros.page,
            page_size=filtros.page_size,
        )

        total_pages = math.ceil(total / filtros.page_size) if total > 0 else 1

        return ProductListResponse(
            items=[ProductSummaryResponse.model_validate(p) for p in products],
            total=total,
            page=filtros.page,
            page_size=filtros.page_size,
            total_pages=total_pages,
        )

    def obtener_producto(self, product_id: int) -> ProductDetailResponse:
        """
        Retorna el detalle completo de un producto activo.

        Args:
            product_id: ID del producto a consultar.

        Returns:
            Detalle completo del producto incluyendo categoría y stock.

        Raises:
            ProductoNoEncontradoError: Si el producto no existe o está inactivo.
        """
        product = self.repo.get_product_by_id(product_id)
        if product is None:
            raise ProductoNoEncontradoError(
                f"El producto {product_id} no existe o no está disponible"
            )

        return ProductDetailResponse.model_validate(product)

    def listar_categorias(self) -> list[CategoryResponse]:
        """
        Retorna todas las categorías para poblar el filtro del catálogo.

        Returns:
            Lista de categorías ordenadas alfabéticamente.
        """
        categories = self.repo.list_categories()
        return [CategoryResponse.model_validate(c) for c in categories]

    def verificar_stock(self, product_id: int, cantidad: int) -> bool:
        """
        Verifica si hay stock suficiente para una cantidad dada.

        Usado por el módulo de sales antes de iniciar el checkout,
        para dar feedback temprano al cliente sin procesar el pago.

        Args:
            product_id: ID del producto a verificar.
            cantidad: Unidades a verificar.

        Returns:
            True si hay stock suficiente.
        """
        return self.repo.hay_stock_suficiente(product_id, cantidad)

    def descontar_stock(self, product_id: int, cantidad: int) -> None:
        """
        Descuenta stock al confirmar una compra.

        Llamado exclusivamente por orders/services/order_service.py
        después de que el pago fue confirmado. No debe ser llamado
        desde ningún endpoint HTTP del catálogo.

        El descuento es por orden de compra: si dos clientes compran
        al mismo tiempo, el primero en confirmar obtiene el producto.
        El segundo recibirá StockInsuficienteError en su checkout.

        Args:
            product_id: ID del producto a descontar.
            cantidad: Unidades a restar.

        Raises:
            StockInsuficienteError: Si no hay suficiente stock al momento
                                    de descontar (otra compra se adelantó).
        """
        stock = self.repo.get_stock(product_id)
        disponible = stock.cantidad if stock else 0

        if not self.repo.hay_stock_suficiente(product_id, cantidad):
            raise StockInsuficienteError(
                product_id=product_id,
                disponible=disponible,
                solicitado=cantidad,
            )

        self.repo.descontar_stock(product_id, cantidad)
