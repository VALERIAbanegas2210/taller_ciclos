from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import Optional
from datetime import datetime

class AsignacionBase(BaseModel):
    incidente_id: UUID
    taller_id: UUID
    precio_cotizado: float
    tiempo_estimado_min: int
    nota_taller: Optional[str] = None

class AsignacionCreate(AsignacionBase):
    pass

class AsignacionResponse(AsignacionBase):
    id: UUID
    tecnico_id: Optional[UUID] = None
    estado: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)