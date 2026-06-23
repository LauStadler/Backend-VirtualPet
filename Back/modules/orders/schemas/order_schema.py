"""
Schemas Pydantic del módulo orders.

Cubre dos casos de uso distintos:
  - Cliente: ver sus propias órdenes y su estado actual.
  - Backoffice: ver todas las órdenes y avanzar su estado.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from modules.orders.models.order import OrderEstado


class OrderItemResponse(BaseModel):
    """Detalle de un producto dentro de una orden."""

    product_id: int
    cantidad: int
    precio_unitario: float
    subtotal: float
    producto_nombre: Optional[str] = None
    producto_imagen_url: Optional[str] = None

    model_config = {"from_attributes": True}


class UserSummary(BaseModel):
    """Resumen de datos del cliente para el backoffice."""
    id: int
    nombre: str
    apellido: str
    email: str

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    """
    Representación de una orden para el cliente.
    Muestra el estado actual, items y total.
    """

    id: int
    estado: OrderEstado
    total: float
    direccion_entrega: str
    items: list[OrderItemResponse]
    created_at: datetime
    updated_at: datetime
    intentos: int = 0
    billing_cuit: Optional[str] = None
    billing_requested_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class OrderSummaryResponse(BaseModel):
    """
    Versión resumida de una orden para el listado.
    No incluye el detalle de items para reducir el tamaño de la respuesta
    cuando se listan múltiples órdenes.
    """

    id: int
    estado: OrderEstado
    total: float
    created_at: datetime
    billing_cuit: Optional[str] = None
    billing_requested_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class CambiarEstadoRequest(BaseModel):
    """
    Body para el endpoint PATCH /backoffice/orders/{id}/estado.
    Solo el backoffice puede cambiar estados.
    """

    estado: OrderEstado = Field(
        ...,
        description=(
            "Nuevo estado de la orden. Solo se permiten avances en el flujo: "
            "pendiente → en_preparacion → despachado → en_camino → entregado."
        )
    )


class BackofficeOrderResponse(BaseModel):
    """
    Representación extendida de una orden para el backoffice.
    Incluye datos del cliente para que el equipo de depósito
    pueda identificar a quién pertenece cada pedido.
    """

    id: int
    estado: OrderEstado
    total: float
    direccion_entrega: str
    items: list[OrderItemResponse]
    created_at: datetime
    updated_at: datetime
    user_id: int
    user: Optional[UserSummary] = None
    rider_id: Optional[int] = None
    rider: Optional[UserSummary] = None
    intentos: int = 0
    billing_cuit: Optional[str] = None
    billing_requested_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
