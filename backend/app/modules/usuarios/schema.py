from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID

# ── Registro ─────────────────────────────────────────
class UsuarioCreate(BaseModel):
    nombres: str
    apellidos: str
    email: EmailStr
    telefono: Optional[str] = None
    password: str
    tipo: Optional[str] = "cliente"

# ── Actualizar ────────────────────────────────────────
class UsuarioUpdate(BaseModel):
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    telefono: Optional[str] = None
    foto_perfil_url: Optional[str] = None

# ── Respuesta ─────────────────────────────────────────
class UsuarioOut(BaseModel):
    id: UUID              # ← UUID en vez de str
    nombres: str
    apellidos: str
    email: str
    telefono: Optional[str] = None
    tipo: str
    activo: bool
    foto_perfil_url: Optional[str] = None

    model_config = {"from_attributes": True}

# ── Login ─────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# ── Tokens ────────────────────────────────────────────
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    usuario: UsuarioOut

class RefreshRequest(BaseModel):
    refresh_token: str