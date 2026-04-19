from sqlalchemy.orm import Session
from .models import Incidente
from .schema import IncidenteCreate
from uuid import UUID  # Importante

# Cambiamos usuario_id: int a usuario_id: str o UUID
def create_incidente(db: Session, incidente: IncidenteCreate, usuario_id: str):
    db_incidente = Incidente(
        **incidente.dict(),
        usuario_id=usuario_id, 
        estado="pendiente"
    )
    db.add(db_incidente)
    db.commit()
    db.refresh(db_incidente)
    return db_incidente