"""
Servicio de autenticación.

Contiene toda la lógica de negocio relacionada con el acceso al sistema:
registro de usuarios, login, y generación de tokens JWT.

Regla de diseño: este servicio no conoce nada de HTTP (no importa FastAPI).
Si necesitás levantar un error HTTP, lo hace el controller — este servicio
lanza excepciones de dominio propias que el controller traduce.
"""

from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional

from modules.auth.repositories.user_repository import UserRepository
from modules.auth.models.user import User, UserRole
from modules.auth.schemas.user_schema import (
    RegisterRequest, 
    LoginRequest, 
    CreateUserAdminRequest,
    UpdateProfileRequest,
    ChangePasswordRequest
)
from shared.utils.security import hash_password, verify_password, create_access_token
from shared.config.settings import settings


class EmailYaRegistradoError(Exception):
    """Se lanza cuando se intenta registrar un email que ya existe en el sistema."""
    pass


class CredencialesInvalidasError(Exception):
    """Se lanza cuando el email no existe o la contraseña es incorrecta."""
    pass


class UsuarioInactivoError(Exception):
    """Se lanza cuando el usuario existe pero fue desactivado por un admin."""
    pass


class UsuarioNoEncontradoError(Exception):
    """Se lanza cuando se busca un usuario por ID y no existe."""
    pass


class IAuthService(ABC):
    """Interfaz para el servicio de autenticación."""

    @abstractmethod
    def registrar_cliente(self, datos: RegisterRequest) -> tuple[User, str]:
        pass

    @abstractmethod
    def login(self, datos: LoginRequest) -> tuple[User, str]:
        pass

    @abstractmethod
    def crear_usuario_admin(self, datos: CreateUserAdminRequest) -> User:
        pass

    @abstractmethod
    def listar_usuarios(self, role: Optional[UserRole] = None) -> list[User]:
        pass

    @abstractmethod
    def eliminar_usuario(self, user_id: int) -> User:
        pass

    @abstractmethod
    def obtener_perfil(self, user_id: int) -> User:
        pass

    @abstractmethod
    def actualizar_perfil(self, user_id: int, datos: UpdateProfileRequest) -> User:
        pass

    @abstractmethod
    def cambiar_contrasena(self, user_id: int, datos: ChangePasswordRequest) -> None:
        pass


class AuthService(IAuthService):
    """Lógica de negocio para autenticación y gestión de usuarios."""

    def __init__(self, db: Session) -> None:
        """
        Args:
            db: Sesión de base de datos inyectada por FastAPI.
        """
        self.repo = UserRepository(db)

    def registrar_cliente(self, datos: RegisterRequest) -> tuple[User, str]:
        """
        Registra un nuevo cliente en el sistema.

        Valida que el email no esté en uso, hashea la contraseña,
        y crea el usuario con rol CLIENTE.

        Args:
            datos: Datos del formulario de registro validados por Pydantic.

        Returns:
            Tupla con (usuario_creado, access_token).

        Raises:
            EmailYaRegistradoError: Si el email ya está registrado.
        """
        if self.repo.email_exists(datos.email):
            raise EmailYaRegistradoError(
                f"El email '{datos.email}' ya está registrado en el sistema"
            )

        password_hash = hash_password(datos.password)

        user = self.repo.create(
            nombre=datos.nombre,
            apellido=datos.apellido,
            email=datos.email,
            password_hash=password_hash,
            role=UserRole.CLIENTE,
        )

        token = create_access_token(user_id=user.id, role=user.role)
        return user, token

    def login(self, datos: LoginRequest) -> tuple[User, str]:
        """
        Autentica un usuario existente y genera un JWT.
        """
        user = self.repo.get_by_email(datos.email)

        # Seguridad: no especificar si falló el email o la contraseña para evitar enumeración.
        msg_error = "Email o contraseña incorrectos."

        if not user:
            raise CredencialesInvalidasError(msg_error)

        if not verify_password(datos.password, user.password_hash):
            raise CredencialesInvalidasError(msg_error)

        if not user.activo:
            raise UsuarioInactivoError(
                "Tu cuenta está desactivada. Contactá al soporte de Virtual Pet."
            )

        token = create_access_token(user_id=user.id, role=user.role)
        return user, token

    def crear_usuario_admin(self, datos: CreateUserAdminRequest) -> User:
        """
        Crea un usuario con cualquier rol. Solo puede llamarlo un ADMIN.
        La validación del rol del llamador se hace en el controller con require_role().

        Permite crear empleados de depósito u otros administradores
        sin pasar por el flujo de registro público.

        Args:
            datos: Datos del nuevo usuario incluyendo el rol a asignar.

        Returns:
            El usuario creado.

        Raises:
            EmailYaRegistradoError: Si el email ya está en uso.
        """
        if self.repo.email_exists(datos.email):
            raise EmailYaRegistradoError(
                f"El email '{datos.email}' ya está registrado en el sistema"
            )

        password_hash = hash_password(datos.password)

        return self.repo.create(
            nombre=datos.nombre,
            apellido=datos.apellido,
            email=datos.email,
            password_hash=password_hash,
            role=datos.role,
        )

    def listar_usuarios(self, role: Optional[UserRole] = None) -> list[User]:
        """
        Retorna la lista de usuarios. Solo debe llamarlo un ADMIN.
        """
        return self.repo.get_all(role=role)

    def eliminar_usuario(self, user_id: int) -> User:
        """
        Desactiva un usuario por su ID. Solo debe llamarlo un ADMIN.
        """
        user = self.repo.get_by_id(user_id)
        if not user:
            raise UsuarioNoEncontradoError(f"No se encontró el usuario con ID {user_id}")
        
        return self.repo.deactivate(user)

    def obtener_perfil(self, user_id: int) -> User:
        """
        Retorna el perfil del usuario autenticado.

        Args:
            user_id: ID del usuario extraído del JWT por el middleware.

        Returns:
            El objeto User con todos sus datos.
        """
        return self.repo.get_by_id(user_id)

    def actualizar_perfil(self, user_id: int, datos: UpdateProfileRequest) -> User:
        """
        Actualiza los datos básicos del perfil.
        """
        user = self.repo.get_by_id(user_id)
        if not user:
            raise UsuarioNoEncontradoError("Usuario no encontrado")

        if datos.nombre:
            user.nombre = datos.nombre
        if datos.apellido:
            user.apellido = datos.apellido

        self.repo.db.commit()
        self.repo.db.refresh(user)
        return user

    def cambiar_contrasena(self, user_id: int, datos: ChangePasswordRequest) -> None:
        """
        Cambia la contraseña del usuario tras verificar la actual.
        """
        user = self.repo.get_by_id(user_id)
        if not user:
            raise UsuarioNoEncontradoError("Usuario no encontrado")

        if not verify_password(datos.current_password, user.password_hash):
            raise CredencialesInvalidasError("La contraseña actual es incorrecta")

        user.password_hash = hash_password(datos.new_password)
        self.repo.db.commit()
