"""
Controller del backoffice.

Endpoints exclusivos para el equipo de depósito y administradores.
Todos requieren rol DEPOSITO o ADMIN — ninguno es accesible por clientes.

No duplica lógica de negocio: delega todo a OrderService del módulo orders.
La separación en este controller es solo de acceso y presentación.

Endpoints:
    GET   /backoffice/orders            → todas las órdenes del sistema
    GET   /backoffice/orders/{id}       → detalle de cualquier orden
    PATCH /backoffice/orders/{id}/estado → avanzar estado de una orden
"""

from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from shared.dependencies.database import get_db
from shared.dependencies.auth import require_role
from shared.utils.websocket_manager import manager
from modules.orders.services.order_service import (
    OrderService,
    OrdenNoEncontradaError,
    TransicionEstadoInvalidaError,
)
from modules.orders.schemas.order_schema import BackofficeOrderResponse, CambiarEstadoRequest
from modules.auth.models.user import UserRole

router = APIRouter()

# Dependencia reutilizable para todos los endpoints del backoffice
_requiere_deposito_o_admin = Depends(require_role(UserRole.DEPOSITO, UserRole.ADMIN))


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    print("New WS connection attempt...")
    await manager.connect(websocket)
    try:
        while True:
            # Mantener la conexión abierta
            await websocket.receive_text()
    except WebSocketDisconnect:
        print("WS Client disconnected via WebSocketDisconnect")
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WS Unexpected error: {e}")
        manager.disconnect(websocket)


@router.get(
    "/orders",
    response_model=list[BackofficeOrderResponse],
    summary="Listar todos los pedidos",
    description=(
        "Retorna todas las órdenes del sistema ordenadas por fecha descendente. "
        "Incluye datos del cliente y detalle de items."
    ),
)
def list_all_orders(
    db: Session = Depends(get_db),
    _=_requiere_deposito_o_admin,
) -> list[BackofficeOrderResponse]:
    """Requiere: JWT con rol DEPOSITO o ADMIN."""
    service = OrderService(db)
    return service.listar_todas()


@router.get(
    "/orders/{order_id}",
    response_model=BackofficeOrderResponse,
    summary="Detalle de cualquier pedido",
    description="Retorna el detalle completo de una orden, sin importar a qué cliente pertenece.",
)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    _=_requiere_deposito_o_admin,
) -> BackofficeOrderResponse:
    """Requiere: JWT con rol DEPOSITO o ADMIN."""
    service = OrderService(db)
    try:
        orders = service.listar_todas()
        order = next((o for o in orders if o.id == order_id), None)
        if order is None:
            raise OrdenNoEncontradaError(f"La orden {order_id} no existe.")
        return order
    except OrdenNoEncontradaError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch(
    "/orders/{order_id}/estado",
    response_model=BackofficeOrderResponse,
    summary="Cambiar estado de un pedido",
    description=(
        "Avanza el estado de una orden al siguiente paso del flujo. "
        "Los estados solo pueden avanzar — nunca retroceder ni saltearse pasos. "
        "Flujo: pendiente → en_preparacion → despachado → en_camino → entregado."
    ),
)
async def cambiar_estado(
    order_id: int,
    body: CambiarEstadoRequest,
    db: Session = Depends(get_db),
    _=_requiere_deposito_o_admin,
) -> BackofficeOrderResponse:
    """
    Requiere: JWT con rol DEPOSITO o ADMIN.

    Retorna 409 si el estado solicitado no es el siguiente válido en el flujo.
    Retorna 404 si la orden no existe.
    """
    service = OrderService(db)
    try:
        order = service.cambiar_estado(order_id=order_id, nuevo_estado=body.estado)
        # Notificar vía WebSocket
        await manager.broadcast({
            "type": "order_updated",
            "order": order.model_dump(mode='json')
        })
        return order
    except OrdenNoEncontradaError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except TransicionEstadoInvalidaError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
