from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from uuid import UUID
from decimal import Decimal


class TallerCreate(BaseModel):
    nombre:            str
    email:             EmailStr
    password:          str
    telefono:          Optional[str]     = None
    direccion:         Optional[str]     = None
    radio_servicio_km: Optional[Decimal] = Decimal("10")
    descripcion:       Optional[str]     = None
    latitud:           Optional[float]   = None
    longitud:          Optional[float]   = None

    @field_validator("nombre")
    @classmethod
    def nombre_no_vacio(cls, v):
        if not v or not v.strip():
            raise ValueError("El nombre no puede estar vacío")
        return v.strip()

    @field_validator("password")
    @classmethod
    def password_min(cls, v):
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        return v

    @field_validator("radio_servicio_km")
    @classmethod
    def radio_positivo(cls, v):
        if v is not None and v <= 0:
            raise ValueError("El radio de servicio debe ser mayor a 0")
        return v


class TallerUpdate(BaseModel):
    nombre:            Optional[str]     = None
    telefono:          Optional[str]     = None
    direccion:         Optional[str]     = None
    radio_servicio_km: Optional[Decimal] = None
    descripcion:       Optional[str]     = None
    latitud:           Optional[float]   = None
    longitud:          Optional[float]   = None
    activo:            Optional[bool]    = None


class TallerOut(BaseModel):
    id:                UUID
    nombre:            str
    email:             str
    telefono:          Optional[str]     = None
    direccion:         Optional[str]     = None
    radio_servicio_km: Optional[Decimal] = None
    logo_url:          Optional[str]     = None
    descripcion:       Optional[str]     = None
    activo:            bool
    verificado:        bool
    comision_pct:      Decimal

    model_config = {"from_attributes": True}


class TallerLoginRequest(BaseModel):
    email:    EmailStr
    password: str


class LogoTallerOut(BaseModel):
    logo_url: str
    mensaje:  str = "Logo actualizado correctamente"