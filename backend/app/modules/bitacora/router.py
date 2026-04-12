from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user, require_roles
from app.modules.bitacora import service
from app.modules.bitacora.schema import BitacoraListOut

router = APIRouter(prefix="/bitacora", tags=["Bitácora"])

@router.get("/", response_model=BitacoraListOut)
def listar(
    db: Session = Depends(get_db),
    _=Depends(require_roles("admin", "tecnico", "cliente"))
):
    return service.listar_bitacora(db)