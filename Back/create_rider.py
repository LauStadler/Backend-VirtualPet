"""
Script rápido para crear un usuario con rol de Repartidor (DELIVERY).
Ejecutar desde la carpeta 'Back'.
"""
from sqlalchemy.orm import Session
from infrastructure.db.base_class import Base
from infrastructure.db.base import User
from modules.auth.models.user import UserRole
from shared.dependencies.database import SessionLocal
from shared.utils.security import hash_password

def create_rider():
    db = SessionLocal()
    try:
        email = "rider@virtualpet.com"
        # Verificar si ya existe
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"El usuario {email} ya existe.")
            return

        new_rider = User(
            nombre="Juan",
            apellido="Delivery",
            email=email,
            password_hash=hash_password("rider123"),
            role=UserRole.DELIVERY,
            activo=True
        )

        db.add(new_rider)
        db.commit()
        print(f"✅ Rider creado exitosamente!")
        print(f"Email: {email}")
        print(f"Password: rider123")
        
    except Exception as e:
        print(f"❌ Error al crear el rider: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_rider()
