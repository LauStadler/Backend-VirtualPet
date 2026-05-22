"""
Schemas Pydantic del módulo catalog.

Todos los schemas son de solo lectura (response) ya que el catálogo
no acepta escritura desde la API — eso es responsabilidad del ERP externo.

Los schemas de query (filtros) se usan como parámetros de URL en los
endpoints de listado y búsqueda.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CategoryResponse(BaseModel):
    """Representación pública de una categoría."""

    id: int
    nombre: str
    descripcion: Optional[str] = None
    parent_id: Optional[int] = None
    """ID de la categoría padre. Null si es categoría raíz."""

    model_config = {"from_attributes": True}


class StockResponse(BaseModel):
    """Stock disponible de un producto. Se incluye en el detalle del producto."""

    cantidad: int
    """Unidades disponibles. El cliente ve este número en la página del producto."""

    model_config = {"from_attributes": True}


class ProductSummaryResponse(BaseModel):
    """
    Versión resumida de un producto para el listado del catálogo.
    No incluye la descripción larga para reducir el tamaño de la respuesta
    cuando se listan múltiples productos.
    """

    id: int
    nombre: str
    precio: float
    imagen_url: Optional[str] = None
    category_id: Optional[int] = None
    stock: Optional[StockResponse] = None
    """
    Stock incluido en el listado para que el frontend pueda mostrar
    'Sin stock' directamente sin hacer un request adicional por producto.
    """

    model_config = {"from_attributes": True}


class ProductDetailResponse(BaseModel):
    """
    Versión completa de un producto para la página de detalle.
    Incluye descripción, categoría completa y stock.
    """

    id: int
    nombre: str
    descripcion: Optional[str] = None
    precio: float
    imagen_url: Optional[str] = None
    activo: bool
    category: Optional[CategoryResponse] = None
    stock: Optional[StockResponse] = None
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    """
    Wrapper paginado para el listado de productos.
    Incluye metadatos de paginación para que el frontend
    pueda implementar 'cargar más' o paginación numérica.
    """

    items: list[ProductSummaryResponse]
    total: int = Field(..., description="Total de productos que coinciden con el filtro")
    page: int = Field(..., description="Página actual (base 1)")
    page_size: int = Field(..., description="Cantidad de items por página")
    total_pages: int = Field(..., description="Total de páginas disponibles")


class ProductFilterParams(BaseModel):
    """
    Parámetros de filtrado y paginación para el listado de productos.
    Se reciben como query params en GET /catalog/products.

    Ejemplo: GET /catalog/products?categoria_id=3&busqueda=royal&page=2
    """

    busqueda: Optional[str] = Field(
        default=None,
        description="Texto libre para buscar en nombre y descripción del producto"
    )
    categoria_id: Optional[int] = Field(
        default=None,
        description="Filtrar por categoría. Incluye productos de subcategorías."
    )
    solo_con_stock: bool = Field(
        default=True,
        description="Si True, excluye productos sin stock disponible. "
                    "Por defecto True para no mostrar productos agotados."
    )
    page: int = Field(default=1, ge=1, description="Número de página (base 1)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items por página, máximo 100")
