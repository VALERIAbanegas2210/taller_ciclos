from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from . import service, schema

router = APIRouter(prefix="/asignaciones", tags=["asignaciones"])

@router.post("/", response_model=schema.AsignacionResponse)
def crear_asignacion(
    asignacion: schema.AsignacionCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Solo técnicos pueden atender incidentes
    if current_user.tipo not in ['tecnico', 'admin']:
        raise HTTPException(status_code=403, detail="Solo técnicos pueden atender incidentes")
        
    return service.atender_incidente(db, asignacion, current_user.id)