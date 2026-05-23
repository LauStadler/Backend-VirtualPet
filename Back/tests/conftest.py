import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from main import app
from shared.dependencies.database import get_db
from infrastructure.db.base import Base

# Configuración de base de datos SQLite para tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # Crear tablas
    Base.metadata.create_all(bind=engine)
    yield
    # Borrar tablas al finalizar la sesión de tests
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def auth_client(client, db_session):
    from modules.auth.services.auth_service import AuthService
    from modules.auth.schemas.user_schema import RegisterRequest
    
    service = AuthService(db_session)
    datos = RegisterRequest(
        nombre="Test",
        apellido="User",
        email="test_auth@email.com",
        password="password123"
    )
    user, token = service.registrar_cliente(datos)
    client.headers = {"Authorization": f"Bearer {token}"}
    return client, user

@pytest.fixture
def admin_client(client, db_session):
    from modules.auth.services.auth_service import AuthService
    from modules.auth.schemas.user_schema import CreateUserAdminRequest
    from modules.auth.models.user import UserRole
    from shared.utils.security import create_access_token
    
    service = AuthService(db_session)
    datos = CreateUserAdminRequest(
        nombre="Admin",
        apellido="User",
        email="admin@email.com",
        password="password123",
        role=UserRole.ADMIN
    )
    user = service.crear_usuario_admin(datos)
    token = create_access_token(user_id=user.id, role=user.role)
    client.headers = {"Authorization": f"Bearer {token}"}
    return client, user
