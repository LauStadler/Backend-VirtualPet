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
