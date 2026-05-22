"""
Schemas Pydantic del módulo auth.

Los schemas definen la forma de los datos que entran y salen de la API.
Separan la representación HTTP del modelo de base de datos, lo que permite
cambiar uno sin afectar el otro.

Convención de nombres:
- *Request  → datos que llegan del cliente (body del POST/PUT)
- *Response → datos que se devuelven al cliente
- *DB       → datos que se usan internamente entre capas
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from modules.auth.models.user import UserRole


class RegisterRequest(BaseModel):
    """
    Datos requeridos para registrar un nuevo usuario.
    Solo clientes pueden registrarse por esta vía.
    Los usuarios de depósito y admin los crea un administrador.
    """
    nombre: str = Field(..., min_length=2, max_length=100, examples=["Juan"])
    apellido: str = Field(..., min_length=2, max_length=100, examples=["Pérez"])
    email: EmailStr = Field(..., examples=["juan@email.com"])
    password: str = Field(..., min_length=8, max_length=64, examples=["miPassword123"])

    @field_validator("password")
    @classmethod
    def password_must_have_number(cls, v: str) -> str:
        """La contraseña debe tener al menos un número para mayor seguridad."""
        if not any(char.isdigit() for char in v):
            raise ValueError("La contraseña debe contener al menos un número")
        return v


class LoginRequest(BaseModel):
    """Credenciales para autenticar un usuario existente."""
    email: EmailStr = Field(..., examples=["juan@email.com"])
    password: str = Field(..., examples=["miPassword123"])


class TokenResponse(BaseModel):
    """
    Respuesta exitosa al hacer login o registro.
    El access_token debe incluirse en el header Authorization de
    cada request posterior: 'Authorization: Bearer <token>'
    """
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Segundos hasta que expira el token")
    user: "UserResponse"


class UserResponse(BaseModel):
    """
    Representación pública de un usuario.
    Nunca incluye password_hash ni datos sensibles.
    """
    id: int
    nombre: str
    apellido: str
    email: str
    role: UserRole
    activo: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class CreateUserAdminRequest(BaseModel):
    """
    Schema para que un ADMIN cree usuarios con cualquier rol.
    Permite crear empleados de depósito u otros admins.
    """
    nombre: str = Field(..., min_length=2, max_length=100)
    apellido: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=64)
    role: UserRole = Field(..., description="Rol a asignar al nuevo usuario")


# Necesario para que TokenResponse pueda referenciar UserResponse
TokenResponse.model_rebuild()
