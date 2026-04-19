from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.dependencies import get_db, get_current_user
from . import service, schema

router = APIRouter(prefix="/asignaciones", tags=["asignaciones"])

@router.post("/", response_model=schema.AsignacionResponse)
def crear_asignacion(
    asignacion: schema.AsignacionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.tipo not in ['tecnico', 'admin']:
        raise HTTPException(status_code=403, detail="Solo técnicos pueden atender incidentes")
    return service.atender_incidente(db, asignacion, current_user.id)


@router.get("/disponibles", response_model=List[schema.IncidenteDisponibleOut])
def ver_disponibles(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.tipo not in ['tecnico', 'admin']:
        raise HTTPException(status_code=403, detail="No autorizado")
    return service.obtener_disponibles(db)