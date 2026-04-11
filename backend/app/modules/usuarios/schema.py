from pydantic import BaseModel, EmailStr
from typing import Optional

# 📝 Registro
class UsuarioCreate(BaseModel):
    nombres: str
    apellidos: str
    email: EmailStr
    telefono: Optional[str] = None
    password: str
    tipo: str  # cliente | tecnico

# 🔐 Login
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    tipo: str

# 👤 Usuario response
class UsuarioResponse(BaseModel):
    id: str
    nombres: str
    apellidos: str
    email: str
    telefono: Optional[str]
    tipo: str
    activo: bool

    

class UsuarioUpdate(BaseModel):
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    password: Optional[str] = None
    tipo: Optional[str] = None

class UsuarioOut(BaseModel):
    id: str
    nombres: str
    apellidos: str
    email: str
    telefono: Optional[str]
    tipo: str
    activo: bool

class Config:
    from_attributes = True

class RefreshRequest(BaseModel):
    refresh_token: str