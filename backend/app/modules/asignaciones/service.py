from sqlalchemy.orm import Session
from .models import Asignacion
from .schema import AsignacionCreate
from app.modules.incidentes.models import Incidente
from uuid import UUID

def atender_incidente(db: Session, asignacion_data: AsignacionCreate, user_id: UUID):
    # 1. Crear la asignación
    db_asignacion = Asignacion(
        **asignacion_data.model_dump(),
        tecnico_id=user_id, # El técnico que lo toma
        estado="aceptada",
        aceptado_at=datetime.utcnow()
    )
    db.add(db_asignacion)
    
    # 2. Actualizar el estado del incidente a 'en_proceso'
    incidente = db.query(Incidente).filter(Incidente.id == asignacion_data.incidente_id).first()
    if incidente:
        incidente.estado = "en_proceso"
    
    db.commit()
    db.refresh(db_asignacion)
    return db_asignacion