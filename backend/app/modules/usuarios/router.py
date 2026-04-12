from fastapi import APIRouter, Depends, Request
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
from app.modules.bitacora import service as bitacora_service

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.post("/registro", response_model=UsuarioOut, status_code=201)
def registro(data: UsuarioCreate, db: Session = Depends(get_db)):
    return service.crear_usuario(db, data)

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    result = service.login(db, data.email, data.password)
    # Registrar en bitácora
    bitacora_service.registrar_accion(
        db=db,
        usuario=result["usuario"],
        accion="login",
        ip=request.client.host
    )
    return result

@router.post("/logout")
def logout(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    bitacora_service.registrar_accion(
        db=db,
        usuario=current_user,
        accion="logout"
    )
    return {"detail": "Sesión cerrada correctamente"}

@router.post("/refresh", response_model=TokenResponse)
def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    return service.refresh_token(db, data.refresh_token)

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