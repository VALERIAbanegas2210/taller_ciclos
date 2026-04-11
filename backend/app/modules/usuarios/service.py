from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.modules.usuarios.models import Usuario
from app.modules.usuarios.schema import UsuarioCreate, UsuarioUpdate
from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token
)
import uuid

ROLES_VALIDOS = {"cliente", "admin", "tecnico"}

def crear_usuario(db: Session, data: UsuarioCreate) -> Usuario:
    if data.tipo not in ROLES_VALIDOS:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo inválido. Opciones: {list(ROLES_VALIDOS)}"
        )
    if db.query(Usuario).filter(Usuario.email == data.email).first():
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    usuario = Usuario(
        id=uuid.uuid4(),
        nombres=data.nombres,
        apellidos=data.apellidos,
        email=data.email,
        telefono=data.telefono,
        password_hash=hash_password(data.password),
        tipo=data.tipo,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario

def login(db: Session, email: str, password: str) -> dict:
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario or not verify_password(password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    if not usuario.activo:
        raise HTTPException(status_code=403, detail="Cuenta desactivada")

    payload = {"sub": str(usuario.id), "tipo": usuario.tipo}
    return {
        "access_token":  create_access_token(payload),
        "refresh_token": create_refresh_token(payload),
        "token_type":    "bearer",
        "usuario":       usuario,
    }

def refresh_token(db: Session, token: str) -> dict:
    payload = decode_token(token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Refresh token inválido")
    usuario = db.query(Usuario).filter(Usuario.id == payload["sub"]).first()
    if not usuario or not usuario.activo:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    new_payload = {"sub": str(usuario.id), "tipo": usuario.tipo}
    return {
        "access_token":  create_access_token(new_payload),
        "refresh_token": create_refresh_token(new_payload),
        "token_type":    "bearer",
        "usuario":       usuario,
    }

def listar_usuarios(db: Session):
    return db.query(Usuario).all()

def obtener_usuario(db: Session, user_id: str) -> Usuario:
    u = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return u

def actualizar_usuario(db: Session, user_id: str, data: UsuarioUpdate) -> Usuario:
    u = obtener_usuario(db, user_id)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(u, field, value)
    db.commit()
    db.refresh(u)
    return u

def activar_usuario(db: Session, user_id: str) -> Usuario:
    u = obtener_usuario(db, user_id)
    u.activo = True
    db.commit()
    db.refresh(u)
    return u

def desactivar_usuario(db: Session, user_id: str) -> Usuario:
    u = obtener_usuario(db, user_id)
    u.activo = False
    db.commit()
    db.refresh(u)
    return u