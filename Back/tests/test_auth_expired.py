import pytest
from datetime import datetime, timedelta
from jose import jwt
from shared.config.settings import settings
from modules.auth.models.user import UserRole

def test_acceso_con_token_expirado(client):
    """
    Verifica que el sistema rechace con 401 un token que ya expiró.
    """
    # 1. Crear un payload que ya expiró (hace 1 hora)
    expire = datetime.utcnow() - timedelta(hours=1)
    payload = {
        "user_id": 999, # No importa si el usuario existe, el decode fallará por exp
        "role": UserRole.CLIENTE.value,
        "exp": expire
    }
    
    expired_token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    # 2. Intentar acceder a un endpoint protegido
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = client.get("/orders", headers=headers)
    
    # 3. Validar respuesta 401 Unauthorized
    assert response.status_code == 401
    assert "Token inválido o expirado" in response.json()["detail"]

def test_acceso_sin_token(client):
    """
    Verifica que el sistema rechace con 401 si no se envía el header Authorization.
    """
    response = client.get("/orders")
    assert response.status_code == 401
    # FastAPI/OAuth2PasswordBearer devuelve "Not authenticated" por defecto si falta el token
    assert response.json()["detail"] == "Not authenticated"
