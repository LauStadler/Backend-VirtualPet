"""
Controller del módulo auth.

Expone los endpoints HTTP de autenticación. Su única responsabilidad es:
1. Recibir el request HTTP y validar el body con Pydantic.
2. Llamar al servicio correspondiente.
3. Traducir excepciones de dominio a respuestas HTTP adecuadas.
4. Devolver el response serializado.

No contiene lógica de negocio — eso vive en AuthService.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from shared.dependencies.database import get_db
from shared.dependencies.auth import get_current_user, require_role
from shared.config.settings import settings
from modules.auth.services.auth_service import (
    AuthService,
    EmailYaRegistradoError,
    CredencialesInvalidasError,
    UsuarioInactivoError,
    UsuarioNoEncontradoError,
)
from modules.auth.schemas.user_schema import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
    CreateUserAdminRequest,
    UpdateProfileRequest,
    ChangePasswordRequest,
)
from modules.auth.models.user import User, UserRole

router = APIRouter()


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar nuevo cliente",
    description="Crea una cuenta de cliente y devuelve un JWT para autenticar requests posteriores.",
)
def register(body: RegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """
    Endpoint público — no requiere autenticación previa.

    El token retornado tiene una duración de 24 horas.
    Incluirlo en el header: 'Authorization: Bearer <token>'
    """
    service = AuthService(db)
    try:
        user, token = service.registrar_cliente(body)
    except EmailYaRegistradoError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )

    return TokenResponse(
        access_token=token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user),
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Iniciar sesión",
    description="Autentica un usuario existente y devuelve un JWT.",
)
def login(body: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """
    Endpoint público — no requiere autenticación previa.

    En caso de credenciales incorrectas devuelve 401 sin especificar
    si el error es en el email o la contraseña (seguridad anti-enumeración).
    """
    service = AuthService(db)
    try:
        user, token = service.login(body)
    except CredencialesInvalidasError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except UsuarioInactivoError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )

    return TokenResponse(
        access_token=token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user),
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Obtener perfil propio",
    description="Retorna los datos del usuario autenticado según el JWT enviado.",
)
def get_profile(current_user: User = Depends(get_current_user)) -> UserResponse:
    """
    Requiere: JWT válido en el header Authorization.
    Acceso: cualquier usuario autenticado (cliente, depósito, admin).
    """
    return UserResponse.model_validate(current_user)


@router.patch(
    "/me",
    response_model=UserResponse,
    summary="Actualizar perfil propio",
    description="Permite al usuario cambiar su nombre y apellido.",
)
def update_profile(
    body: UpdateProfileRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    service = AuthService(db)
    user = service.actualizar_perfil(current_user.id, body)
    return UserResponse.model_validate(user)


@router.patch(
    "/me/password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cambiar contraseña",
    description="Permite al usuario cambiar su contraseña validando la anterior.",
)
def change_password(
    body: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AuthService(db)
    try:
        service.cambiar_contrasena(current_user.id, body)
    except CredencialesInvalidasError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear usuario (solo admin)",
    description="Permite a un administrador crear usuarios con cualquier rol, "
                "incluyendo empleados de depósito u otros admins.",
)
def create_user(
    body: CreateUserAdminRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
) -> UserResponse:
    """
    Requiere: JWT de usuario con rol ADMIN.
    Acceso: solo administradores.
    """
    service = AuthService(db)
    try:
        user = service.crear_usuario_admin(body)
    except EmailYaRegistradoError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )

    return UserResponse.model_validate(user)


@router.get(
    "/users",
    response_model=list[UserResponse],
    summary="Listar usuarios (solo admin)",
    description="Permite a un administrador ver la lista de todos los usuarios, con opción de filtrar por rol.",
)
def list_users(
    role: Optional[UserRole] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
) -> list[UserResponse]:
    """
    Requiere: JWT de usuario con rol ADMIN.
    """
    service = AuthService(db)
    users = service.listar_usuarios(role=role)
    return [UserResponse.model_validate(u) for u in users]


@router.delete(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="Eliminar usuario (solo admin)",
    description="Permite a un administrador desactivar a un usuario por su ID.",
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
) -> UserResponse:
    """
    Requiere: JWT de usuario con rol ADMIN.
    """
    service = AuthService(db)
    try:
        user = service.eliminar_usuario(user_id)
        return UserResponse.model_validate(user)
    except UsuarioNoEncontradoError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
