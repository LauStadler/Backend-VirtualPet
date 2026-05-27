import pytest
from fastapi import status

def test_register_endpoint(client):
    payload = {
        "nombre": "Juan",
        "apellido": "Perez",
        "email": "juan_api@email.com",
        "password": "password123"
    }
    response = client.post("/auth/register", json=payload)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "juan_api@email.com"

def test_login_endpoint(client):
    # Primero registrar
    payload_reg = {
        "nombre": "Juan",
        "apellido": "Perez",
        "email": "juan_login@email.com",
        "password": "password123"
    }
    client.post("/auth/register", json=payload_reg)
    
    # Login
    payload_login = {
        "email": "juan_login@email.com",
        "password": "password123"
    }
    response = client.post("/auth/login", json=payload_login)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "juan_login@email.com"

def test_get_me_endpoint(client):
    # Registrar y obtener token
    payload_reg = {
        "nombre": "Juan",
        "apellido": "Perez",
        "email": "juan_me@email.com",
        "password": "password123"
    }
    reg_response = client.post("/auth/register", json=payload_reg)
    token = reg_response.json()["access_token"]
    
    # Get me
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/me", headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == "juan_me@email.com"

def test_get_me_unauthorized(client):
    response = client.get("/auth/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_admin_create_user_success(client, db_session):
    # 1. Crear un admin para poder llamar al endpoint
    from modules.auth.models.user import User, UserRole
    from shared.utils.security import hash_password
    
    admin_user = User(
        nombre="Admin",
        apellido="Sist",
        email="admin_test@email.com",
        password_hash=hash_password("admin123"),
        role=UserRole.ADMIN
    )
    db_session.add(admin_user)
    db_session.commit()
    
    # Login para obtener token de admin
    login_res = client.post("/auth/login", json={
        "email": "admin_test@email.com",
        "password": "admin123"
    })
    token = login_res.json()["access_token"]
    
    # 2. Crear un usuario de depósito
    payload = {
        "nombre": "Empleado",
        "apellido": "Deposito",
        "email": "deposito_test@email.com",
        "password": "password123",
        "role": "deposito"
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/auth/users", json=payload, headers=headers)
    
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["email"] == "deposito_test@email.com"
    assert response.json()["role"] == "deposito"

def test_non_admin_cannot_create_user(client, db_session):
    # 1. Crear un usuario común (cliente)
    payload_reg = {
        "nombre": "Cliente",
        "apellido": "Test",
        "email": "cliente_test@email.com",
        "password": "password123"
    }
    reg_res = client.post("/auth/register", json=payload_reg)
    token = reg_res.json()["access_token"]
    
    # 2. Intentar crear otro usuario
    payload = {
        "nombre": "Hack",
        "apellido": "User",
        "email": "hack@email.com",
        "password": "password123",
        "role": "admin"
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/auth/users", json=payload, headers=headers)
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_profile_success(client):
    # Registrar y obtener token
    payload_reg = {
        "nombre": "Original",
        "apellido": "Name",
        "email": "update_me@email.com",
        "password": "password123"
    }
    reg_response = client.post("/auth/register", json=payload_reg)
    token = reg_response.json()["access_token"]
    
    # Update profile
    headers = {"Authorization": f"Bearer {token}"}
    payload_update = {"nombre": "Nuevo", "apellido": "Apellido"}
    response = client.patch("/auth/me", json=payload_update, headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["nombre"] == "Nuevo"
    assert data["apellido"] == "Apellido"


def test_change_password_success(client):
    # Registrar
    payload_reg = {
        "nombre": "User",
        "apellido": "Test",
        "email": "change_pass@email.com",
        "password": "password123"
    }
    client.post("/auth/register", json=payload_reg)
    
    # Login para obtener token
    login_res = client.post("/auth/login", json={
        "email": "change_pass@email.com",
        "password": "password123"
    })
    token = login_res.json()["access_token"]
    
    # Change password
    headers = {"Authorization": f"Bearer {token}"}
    payload_pass = {
        "current_password": "password123",
        "new_password": "newpassword123"
    }
    response = client.patch("/auth/me/password", json=payload_pass, headers=headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Intentar login con password viejo
    login_old = client.post("/auth/login", json={
        "email": "change_pass@email.com",
        "password": "password123"
    })
    assert login_old.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Intentar login con password nuevo
    login_new = client.post("/auth/login", json={
        "email": "change_pass@email.com",
        "password": "newpassword123"
    })
    assert login_new.status_code == status.HTTP_200_OK
