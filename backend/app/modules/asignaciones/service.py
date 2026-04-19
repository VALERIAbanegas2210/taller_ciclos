from sqlalchemy.orm import Session, joinedload
from .models import Asignacion
from .schema import AsignacionCreate
from app.modules.incidentes.models import Incidente
from uuid import UUID
from datetime import datetime  # ✅ FALTABA
from fastapi import HTTPException


def atender_incidente(db: Session, asignacion_data: AsignacionCreate, user_id: UUID):
    incidente = db.query(Incidente).filter(
        Incidente.id == asignacion_data.incidente_id
    ).first()

    if not incidente:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")
    if incidente.estado != "pendiente":
        raise HTTPException(status_code=400, detail="El incidente ya fue tomado")

    db_asignacion = Asignacion(
        **asignacion_data.model_dump(),
        tecnico_id=user_id,
        estado="aceptada",
        aceptado_at=datetime.utcnow()
    )
    db.add(db_asignacion)
    incidente.estado = "en_proceso"
    db.commit()
    db.refresh(db_asignacion)
    return db_asignacion


def obtener_disponibles(db: Session):
    return db.query(Incidente)\
        .options(
            joinedload(Incidente.vehiculo),
            joinedload(Incidente.usuario)
        )\
        .filter(Incidente.estado == "pendiente")\
        .order_by(Incidente.created_at.desc())\
        .all()