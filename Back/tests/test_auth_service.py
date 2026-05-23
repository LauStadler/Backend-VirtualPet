import pytest
from modules.auth.services.auth_service import AuthService, EmailYaRegistradoError, CredencialesInvalidasError
from modules.auth.schemas.user_schema import RegisterRequest, LoginRequest
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
