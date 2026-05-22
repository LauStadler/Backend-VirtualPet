"""
Controller del módulo catalog.

Expone endpoints de solo lectura para el catálogo de productos.
No hay endpoints de escritura — el ERP externo gestiona los datos
directamente en MySQL.

Endpoints públicos (sin autenticación):
    GET /catalog/products         → listado paginado con filtros
    GET /catalog/products/{id}    → detalle de un producto
    GET /catalog/categories       → listado de categorías para filtros
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from shared.dependencies.database import get_db
from modules.catalog.services.catalog_service import CatalogService, ProductoNoEncontradoError
from modules.catalog.schemas.catalog_schema import (
    ProductListResponse,
    ProductDetailResponse,
    ProductFilterParams,
    CategoryResponse,
)

router = APIRouter()


@router.get(
    "/products",
    response_model=ProductListResponse,
    summary="Listar productos del catálogo",
    description=(
        "Retorna el catálogo de productos activos con filtros opcionales. "
        "Endpoint público — no requiere autenticación. "
        "Por defecto solo muestra productos con stock disponible."
    ),
)
def list_products(
    db: Session = Depends(get_db),
    busqueda: Optional[str] = Query(
        default=None,
        description="Texto para buscar en nombre y descripción"
    ),
    categoria_id: Optional[int] = Query(
        default=None,
        description="Filtrar por ID de categoría"
    ),
    solo_con_stock: bool = Query(
        default=True,
        description="Si True, oculta productos sin stock"
    ),
    page: int = Query(default=1, ge=1, description="Número de página"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items por página"),
) -> ProductListResponse:
    """
    Endpoint público — no requiere autenticación.

    Soporta búsqueda por texto libre, filtrado por categoría y paginación.
    Incluye el stock de cada producto para que el frontend pueda mostrar
    disponibilidad sin requests adicionales.
    """
    filtros = ProductFilterParams(
        busqueda=busqueda,
        categoria_id=categoria_id,
        solo_con_stock=solo_con_stock,
        page=page,
        page_size=page_size,
    )
    service = CatalogService(db)
    return service.listar_productos(filtros)


@router.get(
    "/products/{product_id}",
    response_model=ProductDetailResponse,
    summary="Detalle de un producto",
    description=(
        "Retorna la información completa de un producto: descripción, "
        "categoría, precio y stock actual. Endpoint público."
    ),
)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
) -> ProductDetailResponse:
    """
    Endpoint público — no requiere autenticación.

    Retorna 404 si el producto no existe o fue desactivado por el ERP.
    """
    service = CatalogService(db)
    try:
        return service.obtener_producto(product_id)
    except ProductoNoEncontradoError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get(
    "/categories",
    response_model=list[CategoryResponse],
    summary="Listar categorías",
    description=(
        "Retorna todas las categorías disponibles para poblar "
        "el filtro de categorías en el catálogo. Endpoint público."
    ),
)
def list_categories(db: Session = Depends(get_db)) -> list[CategoryResponse]:
    """
    Endpoint público — no requiere autenticación.

    Las categorías son gestionadas por el ERP externo.
    """
    service = CatalogService(db)
    return service.listar_categorias()
