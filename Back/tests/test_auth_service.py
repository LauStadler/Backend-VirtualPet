import pytest
from modules.auth.services.auth_service import (
    AuthService, 
    EmailYaRegistradoError, 
    CredencialesInvalidasError,
    UsuarioNoEncontradoError
)
from modules.auth.schemas.user_schema import (
    RegisterRequest, 
    LoginRequest, 
    UpdateProfileRequest, 
    ChangePasswordRequest
)
from modules.auth.models.user import UserRole

def test_registrar_cliente_exito(db_session):
    service = AuthService(db_session)
    datos = RegisterRequest(
        nombre="Juan",
        apellido="Perez",
        email="juan@email.com",
        password="password123"
    )
    
    user, token = service.registrar_cliente(datos)
    
    assert user.id is not None
    assert user.email == "juan@email.com"
    assert user.role == UserRole.CLIENTE
    assert token is not None

def test_registrar_cliente_email_duplicado(db_session):
    service = AuthService(db_session)
    datos = RegisterRequest(
        nombre="Juan",
        apellido="Perez",
        email="juan@email.com",
        password="password123"
    )
    
    service.registrar_cliente(datos)
    
    with pytest.raises(EmailYaRegistradoError):
        service.registrar_cliente(datos)

def test_login_exito(db_session):
    service = AuthService(db_session)
    # Registrar primero
    datos_reg = RegisterRequest(
        nombre="Juan",
        apellido="Perez",
        email="juan@email.com",
        password="password123"
    )
    service.registrar_cliente(datos_reg)
    
    # Login
    datos_login = LoginRequest(
        email="juan@email.com",
        password="password123"
    )
    user, token = service.login(datos_login)
    
    assert user.email == "juan@email.com"
    assert token is not None

def test_login_credenciales_invalidas(db_session):
    service = AuthService(db_session)
    datos_login = LoginRequest(
        email="noexiste@email.com",
        password="password123"
    )
    
    with pytest.raises(CredencialesInvalidasError):
        service.login(datos_login)


def test_actualizar_perfil_exito(db_session):
    service = AuthService(db_session)
    datos_reg = RegisterRequest(
        nombre="Juan",
        apellido="Perez",
        email="update_service@email.com",
        password="password123"
    )
    user, _ = service.registrar_cliente(datos_reg)
    
    # Actualizar
    datos_update = UpdateProfileRequest(nombre="Juan Carlos", apellido="Perez Garcia")
    updated_user = service.actualizar_perfil(user.id, datos_update)
    
    assert updated_user.nombre == "Juan Carlos"
    assert updated_user.apellido == "Perez Garcia"


def test_cambiar_contrasena_exito(db_session):
    service = AuthService(db_session)
    datos_reg = RegisterRequest(
        nombre="Juan",
        apellido="Perez",
        email="pass_service@email.com",
        password="password123"
    )
    user, _ = service.registrar_cliente(datos_reg)
    
    # Cambiar pass
    datos_pass = ChangePasswordRequest(
        current_password="password123",
        new_password="newpassword123"
    )
    service.cambiar_contrasena(user.id, datos_pass)
    
    # Verificar login con nuevo pass
    user_logged, _ = service.login(LoginRequest(email="pass_service@email.com", password="newpassword123"))
    assert user_logged.id == user.id


def test_cambiar_contrasena_actual_incorrecta(db_session):
    service = AuthService(db_session)
    datos_reg = RegisterRequest(
        nombre="Juan",
        apellido="Perez",
        email="pass_fail@email.com",
        password="password123"
    )
    user, _ = service.registrar_cliente(datos_reg)
    
    datos_pass = ChangePasswordRequest(
        current_password="wrongpassword",
        new_password="newpassword123"
    )
    with pytest.raises(CredencialesInvalidasError):
        service.cambiar_contrasena(user.id, datos_pass)
