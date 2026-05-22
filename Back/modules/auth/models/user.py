"""
Modelo de usuario del sistema Virtual Pet.

Este modelo representa a cualquier persona que interactúa con el sistema,
ya sea un cliente de la tienda, un empleado del depósito, o un administrador.
El rol determina a qué partes del sistema puede acceder cada usuario.
"""

from sqlalchemy import Column, Integer, String, Enum, DateTime, Boolean
from sqlalchemy.sql import func
from infrastructure.db.base_class import Base
import enum


class UserRole(str, enum.Enum):
    """
    Roles disponibles en el sistema.

    - CLIENTE: comprador de la tienda, accede a catálogo, carrito y sus pedidos.
    - DEPOSITO: equipo interno, accede al backoffice para gestionar pedidos.
    - ADMIN: acceso total, puede crear productos y gestionar usuarios.
    """
    CLIENTE = "cliente"
    DEPOSITO = "deposito"
    ADMIN = "admin"


class User(Base):
    """
    Tabla de usuarios del sistema.

    Almacena credenciales, datos de contacto y el rol de cada usuario.
    La contraseña nunca se guarda en texto plano — siempre hasheada con bcrypt.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)

    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)

    email = Column(String(255), unique=True, nullable=False, index=True)
    """Email usado como identificador de login. Debe ser único en el sistema."""

    password_hash = Column(String(255), nullable=False)
    """Contraseña hasheada con bcrypt. Nunca almacenar texto plano."""

    role = Column(
        Enum(UserRole),
        nullable=False,
        default=UserRole.CLIENTE
    )
    """Rol del usuario. Determina los permisos en el sistema."""

    activo = Column(Boolean, default=True, nullable=False)
    """Si es False, el usuario no puede hacer login (baja lógica)."""

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"
