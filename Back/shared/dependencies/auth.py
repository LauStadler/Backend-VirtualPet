"""
Dependencias de autenticación reutilizables en todos los módulos.

Estas funciones se usan con Depends() de FastAPI para proteger endpoints.
FastAPI las ejecuta automáticamente antes de llamar al handler del endpoint.

Uso típico:
    @router.get("/orders")
    def listar_pedidos(current_user = Depends(get_current_user)):
        ...

    @router.get("/backoffice/orders")
    def backoffice(current_user = Depends(require_role(UserRole.DEPOSITO, UserRole.ADMIN))):
        ...
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from shared.config.settings import settings
from shared.dependencies.database import get_db

# Le indica a FastAPI dónde está el endpoint de login para el flujo OAuth2.
# Esto habilita el botón "Authorize" en /docs.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Dependencia que extrae y valida el JWT del header Authorization.

    Decodifica el token, verifica la firma y busca al usuario en la DB.
    Si el token es inválido, expiró, o el usuario no existe, retorna 401.

    Args:
        token: JWT extraído automáticamente del header 'Authorization: Bearer <token>'.
        db: Sesión de base de datos.

    Returns:
        El objeto User correspondiente al token.

    Raises:
        HTTPException 401: Si el token es inválido, expiró, o el usuario no existe.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado. Iniciá sesión nuevamente.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Import aquí para evitar circular imports entre shared y módulos
    from modules.auth.repositories.user_repository import UserRepository
    user = UserRepository(db).get_by_id(user_id)

    if user is None or not user.activo:
        raise credentials_exception

    return user


def require_role(*roles):
    """
    Factoría de dependencias para proteger endpoints por rol.

    Primero valida el JWT con get_current_user, luego verifica
    que el rol del usuario esté entre los permitidos.

    Args:
        *roles: Uno o más UserRole permitidos para acceder al endpoint.

    Returns:
        Una dependencia de FastAPI que retorna el usuario si tiene el rol correcto.

    Raises:
        HTTPException 403: Si el usuario no tiene el rol requerido.

    Ejemplo:
        Depends(require_role(UserRole.ADMIN))
        Depends(require_role(UserRole.DEPOSITO, UserRole.ADMIN))
    """
    # Normalizamos a string para comparar con el valor del enum guardado en DB
    roles_permitidos = {r.value if hasattr(r, "value") else r for r in roles}

    def checker(current_user=Depends(get_current_user)):
        user_role = current_user.role.value if hasattr(current_user.role, "value") else current_user.role
        if user_role not in roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Se requiere uno de los siguientes roles: "
                       f"{', '.join(roles_permitidos)}"
            )
        return current_user

    return checker
