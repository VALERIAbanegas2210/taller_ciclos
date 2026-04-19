from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.dependencies import get_db, get_current_user
from . import service, schema

router = APIRouter(prefix="/incidentes", tags=["incidentes"])

@router.post("/", response_model=schema.IncidenteResponse)
def crear_incidente(
    incidente: schema.IncidenteCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return service.create_incidente(db, incidente, current_user.id)

@router.get("/pendientes", response_model=List[schema.IncidenteResponse])
def listar_pendientes(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Solo técnicos y admin deberían ver los pendientes globales
    if current_user.tipo not in ['tecnico', 'admin']:
        raise HTTPException(status_code=403, detail="No tiene permisos para ver incidentes pendientes")
    return service.get_incidentes_pendientes(db)
#agregado para mandar al talleres

@router.get("/pendientes")
def obtener_pendientes(db: Session = Depends(get_db)):
    return db.query(incidentes).filter(incidentes.estado == "pendiente").all()

