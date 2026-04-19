import uuid
from typing import List

from fastapi import APIRouter, Depends, File, Request, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_roles
from app.modules.usuarios.models import Usuario
from . import service
from .schema import TallerCreate, TallerOut, TallerUpdate, LogoTallerOut

router = APIRouter(prefix="/talleres", tags=["Talleres"])


# ── Rutas públicas ────────────────────────────────────────────────────────────
@router.get("/activos", response_model=List[TallerOut])
def listar_activos(db: Session = Depends(get_db)):
    return service.listar_talleres(db, solo_activos=True)


# ── Taller: registro y perfil propio ─────────────────────────────────────────
@router.post("/registro", response_model=TallerOut, status_code=201)
def registrar(
    data: TallerCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles("tecnico", "admin"))
):
    return service.registrar_taller(db, data)


@router.get("/mi-taller/{taller_id}", response_model=TallerOut)
def mi_taller(
    taller_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles("tecnico", "admin"))
):
    return service.obtener_taller(db, taller_id)


@router.put("/mi-taller/{taller_id}", response_model=TallerOut)
def actualizar_mi_taller(
    taller_id: uuid.UUID,
    data: TallerUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles("tecnico", "admin"))
):
    return service.actualizar_taller(db, taller_id, data)


@router.post("/mi-taller/{taller_id}/logo", response_model=LogoTallerOut)
async def subir_logo(
    taller_id: uuid.UUID,
    request: Request,
    logo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles("tecnico", "admin"))
):
    base_url = str(request.base_url).rstrip("/")
    url = await service.subir_logo(db, taller_id, logo, base_url)
    return LogoTallerOut(logo_url=url)


# ── Admin: gestión completa ───────────────────────────────────────────────────
@router.get("/", response_model=List[TallerOut])
def listar_todos(
    db: Session = Depends(get_db),
    _=Depends(require_roles("admin"))
):
    return service.listar_talleres(db, solo_activos=False)


@router.get("/{taller_id}", response_model=TallerOut)
def obtener(
    taller_id: uuid.UUID,
    db: Session = Depends(get_db),
    _=Depends(require_roles("admin"))
):
    return service.obtener_taller(db, taller_id)


@router.post("/{taller_id}/activar", response_model=TallerOut)
def activar(
    taller_id: uuid.UUID,
    db: Session = Depends(get_db),
    _=Depends(require_roles("admin"))
):
    return service.activar_taller(db, taller_id)


@router.post("/{taller_id}/desactivar", response_model=TallerOut)
def desactivar(
    taller_id: uuid.UUID,
    db: Session = Depends(get_db),
    _=Depends(require_roles("admin"))
):
    return service.desactivar_taller(db, taller_id)


@router.post("/{taller_id}/verificar", response_model=TallerOut)
def verificar(
    taller_id: uuid.UUID,
    db: Session = Depends(get_db),
    _=Depends(require_roles("admin"))
):
    return service.verificar_taller(db, taller_id)