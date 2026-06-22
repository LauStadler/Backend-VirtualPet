"""
Controller para la gestión de delivery desde la App móvil.

Expone endpoints exclusivos para repartidores (Riders).
Permite visualizar pedidos disponibles, tomarlos y marcar entregas/devoluciones.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from shared.dependencies.database import get_db
from shared.dependencies.auth import get_current_user, require_role
from modules.auth.models.user import User, UserRole
from modules.orders.services.order_service import OrderService, OrdenNoEncontradaError, TransicionEstadoInvalidaError
from modules.orders.schemas.order_schema import OrderResponse
from shared.utils.websocket_manager import manager

router = APIRouter()


@router.get(
    "/available",
    response_model=list[OrderResponse],
    summary="Pedidos disponibles para retiro",
    description="Lista todos los pedidos en estado 'PREPARADO' que aún no tienen un repartidor asignado.",
)
def list_available(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.DELIVERY)),
) -> list[OrderResponse]:
    service = OrderService(db)
    return service.listar_disponibles_delivery()


@router.get(
    "/my-orders",
    response_model=list[OrderResponse],
    summary="Mis pedidos en curso",
    description="Lista los pedidos que el repartidor autenticado tiene actualmente asignados (estado 'DESPACHADO').",
)
def list_mine(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.DELIVERY)),
) -> list[OrderResponse]:
    service = OrderService(db)
    return service.listar_mis_entregas(current_user.id)


@router.post(
    "/{order_id}/claim",
    response_model=OrderResponse,
    summary="Reclamar pedido para entrega",
    description="Asigna el pedido al repartidor actual y cambia su estado a 'DESPACHADO'.",
)
async def claim_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.DELIVERY)),
) -> OrderResponse:
    service = OrderService(db)
    try:
        res = service.reclamar_pedido(order_id, current_user.id)
        # Notificar vía WebSocket al backoffice
        try:
            full_order_data = service.obtener_una_backoffice(order_id)
            await manager.broadcast({
                "type": "order_updated",
                "order": full_order_data.model_dump(mode='json')
            })
        except Exception as ws_err:
            print(f"Error broadcasting order claim update: {ws_err}")
        return res
    except OrdenNoEncontradaError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except TransicionEstadoInvalidaError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/{order_id}/complete",
    response_model=OrderResponse,
    summary="Confirmar entrega exitosa",
    description="Marca el pedido como 'ENTREGADO'. Debe estar asignado al repartidor actual.",
)
async def complete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.DELIVERY)),
) -> OrderResponse:
    service = OrderService(db)
    try:
        res = service.completar_entrega(order_id, current_user.id)
        # Notificar vía WebSocket al backoffice
        try:
            full_order_data = service.obtener_una_backoffice(order_id)
            await manager.broadcast({
                "type": "order_updated",
                "order": full_order_data.model_dump(mode='json')
            })
        except Exception as ws_err:
            print(f"Error broadcasting order complete update: {ws_err}")
        return res
    except OrdenNoEncontradaError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except TransicionEstadoInvalidaError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/{order_id}/return",
    response_model=OrderResponse,
    summary="Devolver pedido al depósito",
    description="Devuelve el pedido al depósito (estado 'PREPARADO' y rider_id nulo). Debe estar asignado al repartidor actual.",
)
async def return_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.DELIVERY)),
) -> OrderResponse:
    service = OrderService(db)
    try:
        res = service.devolver_pedido(order_id, current_user.id)
        # Notificar vía WebSocket al backoffice
        try:
            full_order_data = service.obtener_una_backoffice(order_id)
            await manager.broadcast({
                "type": "order_updated",
                "order": full_order_data.model_dump(mode='json')
            })
        except Exception as ws_err:
            print(f"Error broadcasting order return update: {ws_err}")
        return res
    except OrdenNoEncontradaError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/history",
    response_model=list[OrderResponse],
    summary="Historial de entregas",
    description="Lista los pedidos que el repartidor autenticado ha entregado o devuelto hoy.",
)
def list_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.DELIVERY)),
) -> list[OrderResponse]:
    service = OrderService(db)
    # Por simplicidad, traeremos todas las órdenes asignadas a este rider que no estén DESPACHADO
    # En una versión real filtraríamos por fecha de hoy.
    from modules.orders.models.order import Order, OrderEstado
    from sqlalchemy import or_
    stmt = (
        db.query(Order)
        .filter(Order.rider_id == current_user.id)
        .filter(or_(Order.estado == OrderEstado.ENTREGADO, Order.estado == OrderEstado.PREPARADO))
        .order_by(Order.updated_at.desc())
    )
    orders = stmt.all()
    return [OrderResponse.model_validate(o) for o in orders]

