import sys
import os

# Permitir correr desde la raíz de /Back
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from shared.dependencies.database import SessionLocal
import infrastructure.db.base # Registrar todos los modelos
from modules.auth.models.user import User, UserRole
from modules.catalog.models.product import Product
from modules.orders.models.order import Order, OrderEstado
from modules.orders.models.order_item import OrderItem

def create_test_orders():
    db: Session = SessionLocal()
    try:
        # 1. Buscar o crear un usuario cliente
        user = db.query(User).filter(User.email == "cliente@test.com").first()
        if not user:
            print("❌ No se encontró el usuario cliente de prueba. Asegurate de haber corrido el seed.")
            return

        # 2. Obtener algunos productos
        productos = db.query(Product).limit(5).all()
        if not productos:
            print("❌ No hay productos en la base de datos. Corré el seed primero.")
            return

        print("📦 Generando pedidos de prueba...")

        test_data = [
            {"estado": OrderEstado.PENDIENTE, "direccion": "Av. Colón 1234, Mar del Plata"},
            {"estado": OrderEstado.PENDIENTE, "direccion": "Guemes 2500, Mar del Plata"},
            {"estado": OrderEstado.EN_PREPARACION, "direccion": "San Juan 500, Mar del Plata"},
            {"estado": OrderEstado.EN_PREPARACION, "direccion": "Alvarado 3200, Mar del Plata"},
            {"estado": OrderEstado.PREPARADO,   "direccion": "Rivadavia 150, Mar del Plata"},
        ]

        for i, data in enumerate(test_data):
            # Crear Orden
            nueva_orden = Order(
                user_id=user.id,
                estado=data["estado"],
                total=0, # Se calcula sumando items
                direccion_entrega=data["direccion"]
            )
            db.add(nueva_orden)
            db.flush()

            # Agregar 1 o 2 items aleatorios
            total_orden = 0
            # Usamos productos de forma circular o según el índice
            prod = productos[i % len(productos)]
            item = OrderItem(
                order_id=nueva_orden.id,
                product_id=prod.id,
                cantidad=1,
                precio_unitario=prod.precio,
                subtotal=prod.precio
            )
            db.add(item)
            total_orden += prod.precio

            nueva_orden.total = total_orden
            print(f"   ✓ Pedido #{nueva_orden.id} creado en estado '{data['estado']}'")

        db.commit()
        print("\n✅ ¡Pedidos generados con éxito! Refrescá el tablero en http://localhost:5174")

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_test_orders()
