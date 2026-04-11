from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.dependencies import get_current_user, require_roles
from app.modules.usuarios import service
from app.modules.usuarios.schema import (
    UsuarioCreate, UsuarioUpdate, UsuarioOut,
    LoginRequest, TokenResponse, RefreshRequest
)
from fastapi import APIRouter, HTTPException
from app.modules.usuarios.schema import LoginRequest, TokenResponse
from app.core.security import verify_password, create_access_token


router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

# ── Auth (público) ────────────────────────────────────
@router.post("/registro", response_model=UsuarioOut, status_code=201)
def registro(data: UsuarioCreate, db: Session = Depends(get_db)):
    return service.crear_usuario(db, data)

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    return service.login(db, data.email, data.password)

@router.post("/refresh", response_model=TokenResponse)
def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    return service.refresh_token(db, data.refresh_token)

# ── Perfil propio ─────────────────────────────────────
@router.get("/me", response_model=UsuarioOut)
def mi_perfil(current_user=Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UsuarioOut)
def actualizar_mi_perfil(
    data: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return service.actualizar_usuario(db, str(current_user.id), data)

# ── Admin: gestión de usuarios ────────────────────────
@router.get("/", response_model=List[UsuarioOut])
def listar(db: Session = Depends(get_db), _=Depends(require_roles("admin"))):
    return service.listar_usuarios(db)

@router.get("/{user_id}", response_model=UsuarioOut)
def obtener(user_id: UUID, db: Session = Depends(get_db), _=Depends(require_roles("admin"))):
    return service.obtener_usuario(db, str(user_id))

@router.put("/{user_id}", response_model=UsuarioOut)
def actualizar(user_id: UUID, data: UsuarioUpdate, db: Session = Depends(get_db), _=Depends(require_roles("admin"))):
    return service.actualizar_usuario(db, str(user_id), data)

@router.post("/{user_id}/activar", response_model=UsuarioOut)
def activar(user_id: UUID, db: Session = Depends(get_db), _=Depends(require_roles("admin"))):
    return service.activar_usuario(db, str(user_id))

@router.post("/{user_id}/desactivar", response_model=UsuarioOut)
def desactivar(user_id: UUID, db: Session = Depends(get_db), _=Depends(require_roles("admin"))):
    return service.desactivar_usuario(db, str(user_id))



router = APIRouter(prefix="/auth", tags=["Auth"])

# 🔥 SIMULACIÓN (luego conectas a BD)
fake_user = {
    "email": "admin@test.com",
    "password": "$2b$12$KIXQ4v6z7k8mU1Fz7VJp6uYyH5m9W5z9r1q2e3r4t5y6u7i8o9p0"  # hash
}

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest):

    # 🔎 validar usuario (simulado)
    if data.email != fake_user["email"]:
        raise HTTPException(status_code=400, detail="Usuario no existe")

    if not verify_password(data.password, fake_user["password"]):
        raise HTTPException(status_code=400, detail="Contraseña incorrecta")

    # 🎟️ generar token
    token = create_access_token({"sub": data.email})

    return {
        "access_token": token,
        "token_type": "bearer"
    }

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.modules.usuarios.models import Usuario
from app.modules.usuarios.schema import UsuarioCreate, LoginRequest, TokenResponse, UsuarioResponse
from app.core.security import hash_password, verify_password, create_access_token
from app.dependencies import get_current_user, require_roles

router = APIRouter(prefix="/auth", tags=["Auth"])


# 🔌 DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 📝 REGISTRO
@router.post("/register")
def register(user: UsuarioCreate, db: Session = Depends(get_db)):

    if user.tipo not in ["cliente", "tecnico"]:
        raise HTTPException(status_code=400, detail="Tipo inválido")

    existing = db.query(Usuario).filter(Usuario.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email ya registrado")

    nuevo = Usuario(
        nombres=user.nombres,
        apellidos=user.apellidos,
        email=user.email,
        telefono=user.telefono,
        password_hash=hash_password(user.password),
        tipo=user.tipo
    )

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return {"msg": "Usuario registrado correctamente"}


# 🔐 LOGIN
@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):

    user = db.query(Usuario).filter(Usuario.email == data.email).first()

    if not user:
        raise HTTPException(status_code=400, detail="Usuario no existe")

    if not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Contraseña incorrecta")

    token = create_access_token({
        "sub": user.email,
        "tipo": user.tipo
    })

    return {
        "access_token": token,
        "tipo": user.tipo
    }


# 👤 PERFIL (requiere login)
@router.get("/me", response_model=UsuarioResponse)
def get_me(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(Usuario).filter(Usuario.email == current_user["sub"]).first()
    return user


# 🔒 SOLO CLIENTES
@router.get("/solo-clientes")
def solo_clientes(user=Depends(require_roles("cliente"))):
    return {"msg": "Acceso permitido a clientes"}


# 🔧 SOLO TECNICOS
@router.get("/solo-tecnicos")
def solo_tecnicos(user=Depends(require_roles("tecnico"))):
    return {"msg": "Acceso permitido a técnicos"}


# 👑 SOLO ADMIN
@router.get("/solo-admin")
def solo_admin(user=Depends(require_roles("admin"))):
    return {"msg": "Acceso permitido a admin"}