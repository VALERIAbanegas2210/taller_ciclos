from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import Optional
from datetime import datetime

class IncidenteBase(BaseModel):
    vehiculo_id: UUID
    direccion_texto: str
    ubicacion: Optional[str] = None
    descripcion_manual: str
    categoria: str = "incierto"
    prioridad: str = "media"



class IncidenteCreate(BaseModel):
    vehiculo_id: UUID
    categoria: str
    descripcion_manual: str
    direccion_texto: str
    ubicacion: str = "0,0"
    prioridad: str = "media"

class IncidenteResponse(IncidenteBase):
    id: UUID
    usuario_id: UUID
    estado: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)