import uuid
from decimal import Decimal
from pathlib import Path
from typing import Optional

from fastapi import HTTPException, UploadFile, status
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .models import Taller
from .schema import TallerCreate, TallerUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

UPLOAD_DIR = Path("static/logos_talleres")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

EXTENSIONES_PERMITIDAS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_SIZE_BYTES = 5 * 1024 * 1024


def _get_or_404(db: Session, taller_id: uuid.UUID) -> Taller:
    t = db.query(Taller).filter(Taller.id == taller_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Taller no encontrado")
    return t


def registrar_taller(db: Session, data: TallerCreate) -> Taller:
    if db.query(Taller).filter(Taller.email == data.email).first():
        raise HTTPException(status_code=409, detail="El email ya está registrado")

    taller = Taller(
        id=uuid.uuid4(),
        nombre=data.nombre,
        email=data.email,
        password_hash=pwd_context.hash(data.password),
        telefono=data.telefono,
        direccion=data.direccion,
        radio_servicio_km=data.radio_servicio_km,
        descripcion=data.descripcion,
    )
    db.add(taller)
    db.commit()
    db.refresh(taller)
    return taller


def listar_talleres(db: Session, solo_activos: bool = True):
    q = db.query(Taller)
    if solo_activos:
        q = q.filter(Taller.activo == True)
    return q.all()


def obtener_taller(db: Session, taller_id: uuid.UUID) -> Taller:
    return _get_or_404(db, taller_id)


def actualizar_taller(
    db: Session,
    taller_id: uuid.UUID,
    data: TallerUpdate,
) -> Taller:
    t = _get_or_404(db, taller_id)
    for campo, valor in data.model_dump(exclude_unset=True).items():
        if campo in ("latitud", "longitud"):
            continue  # se manejan aparte si se necesita GEOGRAPHY
        setattr(t, campo, valor)
    db.commit()
    db.refresh(t)
    return t


def activar_taller(db: Session, taller_id: uuid.UUID) -> Taller:
    t = _get_or_404(db, taller_id)
    t.activo = True
    db.commit()
    db.refresh(t)
    return t


def desactivar_taller(db: Session, taller_id: uuid.UUID) -> Taller:
    t = _get_or_404(db, taller_id)
    t.activo = False
    db.commit()
    db.refresh(t)
    return t


def verificar_taller(db: Session, taller_id: uuid.UUID) -> Taller:
    t = _get_or_404(db, taller_id)
    t.verificado = True
    db.commit()
    db.refresh(t)
    return t


async def subir_logo(
    db: Session,
    taller_id: uuid.UUID,
    logo: UploadFile,
    base_url: str,
) -> str:
    t = _get_or_404(db, taller_id)

    ext = Path(logo.filename).suffix.lower()
    if ext not in EXTENSIONES_PERMITIDAS:
        raise HTTPException(
            status_code=422,
            detail=f"Formato no permitido. Usa: {', '.join(EXTENSIONES_PERMITIDAS)}"
        )

    contenido = await logo.read()
    if len(contenido) > MAX_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="El logo supera el límite de 5 MB")

    # Eliminar logo anterior
    if t.logo_url:
        try:
            ruta = Path(t.logo_url.replace(base_url + "/", ""))
            if ruta.exists():
                ruta.unlink(missing_ok=True)
        except Exception:
            pass

    nombre = f"{taller_id}{ext}"
    (UPLOAD_DIR / nombre).write_bytes(contenido)

    url = f"{base_url}/static/logos_talleres/{nombre}"
    t.logo_url = url
    db.commit()
    db.refresh(t)
    return url