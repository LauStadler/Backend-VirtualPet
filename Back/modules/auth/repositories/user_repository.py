"""
Repositorio de usuarios.

Centraliza todas las queries a la tabla 'users'.
Ninguna otra capa del sistema debe hacer queries directas a esta tabla —
siempre deben pasar por este repositorio.

Esto permite:
- Cambiar el ORM o la DB sin tocar servicios ni controllers.
- Tener un único lugar donde buscar queries relacionadas a usuarios.
- Facilitar el mockeo en tests unitarios.
"""

from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional

from modules.auth.models.user import User, UserRole


class UserRepository:
    """Acceso a datos para la entidad User."""

    def __init__(self, db: Session) -> None:
        """
        Args:
            db: Sesión activa de SQLAlchemy, inyectada por FastAPI vía Depends.
        """
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Busca un usuario por su ID primario.

        Args:
            user_id: ID del usuario a buscar.

        Returns:
            El objeto User si existe, None si no se encuentra.
        """
        return self.db.get(User, user_id)

    def get_by_ids(self, user_ids: list[int]) -> list[User]:
        """
        Busca múltiples usuarios por una lista de IDs.
        Útil para la hidratación manual de órdenes.

        Args:
            user_ids: Lista de IDs de usuarios.

        Returns:
            Lista de objetos User encontrados.
        """
        if not user_ids:
            return []
        stmt = select(User).where(User.id.in_(user_ids))
        return list(self.db.scalars(stmt).all())

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Busca un usuario por email. Usado en login y para verificar
        que no exista un email duplicado al registrar.

        Args:
            email: Email a buscar. La búsqueda no es case-sensitive
                   porque el email se guarda en minúsculas al registrar.

        Returns:
            El objeto User si existe, None si no se encuentra.
        """
        stmt = select(User).where(User.email == email.lower())
        return self.db.scalar(stmt)

    def email_exists(self, email: str) -> bool:
        """
        Verifica si un email ya está registrado en el sistema.
        Más eficiente que get_by_email cuando solo se necesita saber si existe.

        Args:
            email: Email a verificar.

        Returns:
            True si el email ya existe, False si está disponible.
        """
        stmt = select(User.id).where(User.email == email.lower())
        return self.db.scalar(stmt) is not None

    def get_all(self, role: Optional[UserRole] = None) -> list[User]:
        """
        Retorna todos los usuarios de la base de datos.

        Args:
            role: Opcional. Si se provee, filtra los usuarios por ese rol.

        Returns:
            Lista de objetos User.
        """
        stmt = select(User)
        if role:
            stmt = stmt.where(User.role == role)
        
        # Ordenar por fecha de creación descendente para ver los más nuevos primero
        stmt = stmt.order_by(User.created_at.desc())
        
        return list(self.db.scalars(stmt).all())

    def create(
        self,
        nombre: str,
        apellido: str,
        email: str,
        password_hash: str,
        role: UserRole = UserRole.CLIENTE
    ) -> User:
        """
        Crea un nuevo usuario en la base de datos.

        El email se normaliza a minúsculas antes de guardar para evitar
        duplicados por diferencias de capitalización (juan@mail.com vs Juan@mail.com).

        Args:
            nombre: Nombre del usuario.
            apellido: Apellido del usuario.
            email: Email del usuario (se guarda en minúsculas).
            password_hash: Contraseña ya hasheada con bcrypt. NUNCA pasar texto plano.
            role: Rol a asignar. Por defecto CLIENTE.

        Returns:
            El objeto User recién creado con su ID asignado por la DB.
        """
        user = User(
            nombre=nombre,
            apellido=apellido,
            email=email.lower(),
            password_hash=password_hash,
            role=role,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def deactivate(self, user: User) -> User:
        """
        Desactiva un usuario (baja lógica). No elimina el registro de la DB
        para preservar el historial de pedidos asociados al usuario.

        Args:
            user: Objeto User a desactivar.

        Returns:
            El objeto User actualizado con activo=False.
        """
        user.activo = False
        self.db.commit()
        self.db.refresh(user)
        return user
