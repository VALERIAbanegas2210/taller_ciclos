from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import Optional
from datetime import datetime

class VehiculoInfo(BaseModel):
    marca:  str
    modelo: str
    anio:   int
    placa:  str
    color:  Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class ClienteInfo(BaseModel):
    nombres:   str
    apellidos: str
    email:     str
    telefono:  Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class IncidenteDisponibleOut(BaseModel):
    id:                UUID
    descripcion_manual: Optional[str] = None
    ubicacion:         Optional[str]  = None
    direccion_texto:   Optional[str]  = None
    categoria:         str
    prioridad:         str
    estado:            str
    created_at:        Optional[datetime] = None
    vehiculo:          Optional[VehiculoInfo] = None
    cliente:           Optional[ClienteInfo]  = None

    model_config = ConfigDict(from_attributes=True)

    @property
    def descripcion(self):
        return self.descripcion_manual

class AsignacionBase(BaseModel):
    incidente_id:        UUID
    taller_id:           UUID
    precio_cotizado:     float
    tiempo_estimado_min: int
    nota_taller:         Optional[str] = None

class AsignacionCreate(AsignacionBase):
    pass

class AsignacionResponse(AsignacionBase):
    id:         UUID
    tecnico_id: Optional[UUID] = None
    estado:     str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)