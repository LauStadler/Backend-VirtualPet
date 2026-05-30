"""
Schemas Pydantic del módulo sales.

El carrito vive en el frontend (cookies/localStorage).
La API solo recibe los items al momento del checkout
y devuelve la orden creada o el error correspondiente.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional


class CartItemRequest(BaseModel):
    """
    Representa un item del carrito enviado por el frontend al hacer checkout.
    El frontend es responsable de mantener estos datos actualizados.
    """

    product_id: int = Field(..., description="ID del producto a comprar")
    cantidad: int = Field(..., ge=1, description="Cantidad a comprar. Mínimo 1.")


class CheckoutRequest(BaseModel):
    """
    Body del endpoint POST /cart/checkout.

    El frontend envía el estado completo del carrito junto con
    la dirección de entrega. La API valida stock y procesa la orden.
    """

    items: list[CartItemRequest] = Field(
        ...,
        min_length=1,
        description="Items del carrito. Debe tener al menos un producto."
    )
    direccion_entrega: str = Field(
        ...,
        min_length=10,
        max_length=300,
        description="Dirección completa de entrega en Mar del Plata"
    )

    @field_validator("items")
    @classmethod
    def no_productos_duplicados(cls, items: list[CartItemRequest]) -> list[CartItemRequest]:
        """
        Valida que no haya dos items con el mismo product_id.
        Si el frontend envía duplicados, es un error de implementación
        que conviene detectar temprano antes de procesar el checkout.
        """
        ids = [item.product_id for item in items]
        if len(ids) != len(set(ids)):
            raise ValueError(
                "El carrito contiene productos duplicados. "
                "Cada producto debe aparecer una sola vez con su cantidad total."
            )
        return items


class CheckoutItemDetail(BaseModel):
    """
    Detalle de un item procesado durante el checkout.
    Se incluye en la respuesta para que el frontend pueda mostrar
    el resumen de la compra con precios confirmados por la API.
    """

    product_id: int
    producto_nombre: str
    producto_imagen_url: Optional[str] = None
    cantidad: int
    precio_unitario: float
    subtotal: float


class CheckoutResponse(BaseModel):
    """
    Respuesta exitosa del checkout.

    Incluye el ID de la orden creada y el detalle de los items
    con precios validados por la API (no los del frontend, que
    pueden estar desactualizados si el ERP actualizó precios).
    """

    orden_id: int
    items: list[CheckoutItemDetail]
    total: float
    direccion_entrega: str
    mensaje: str = "Tu pedido fue confirmado. Te avisaremos cuando esté en camino."
