"""
Controller del módulo orders — endpoints para el cliente.

Expone el historial de compras y el detalle de cada orden.
El cliente solo puede ver sus propias órdenes — nunca las ajenas.

Endpoints:
    GET /orders         → historial de compras del cliente autenticado
    GET /orders/{id}    → detalle de una orden propia con items
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from shared.dependencies.database import get_db
from shared.dependencies.auth import get_current_user
from modules.orders.services.order_service import OrderService, OrdenNoEncontradaError
from modules.orders.schemas.order_schema import OrderResponse, OrderSummaryResponse
from modules.auth.models.user import User

router = APIRouter()


@router.get(
    "",
    response_model=list[OrderSummaryResponse],
    summary="Mis pedidos",
    description=(
        "Retorna el historial de compras del cliente autenticado, "
        "ordenado del más reciente al más antiguo. "
        "Solo incluye resumen — usar GET /orders/{id} para el detalle completo."
    ),
)
def list_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[OrderSummaryResponse]:
    """Requiere: JWT válido de cualquier rol."""
    service = OrderService(db)
    return service.listar_mis_ordenes(user_id=current_user.id)


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    summary="Detalle de un pedido",
    description=(
        "Retorna el detalle completo de una orden: items, precios, "
        "estado actual y dirección de entrega. "
        "Solo el dueño de la orden puede consultarla."
    ),
)
def get_my_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OrderResponse:
    """
    Requiere: JWT válido de cualquier rol.
    Retorna 404 si la orden no existe o no pertenece al usuario autenticado.
    Esto evita que un cliente pueda enumerar órdenes ajenas probando IDs.
    """
    service = OrderService(db)
    try:
        return service.obtener_mi_orden(order_id=order_id, user_id=current_user.id)
    except OrdenNoEncontradaError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
