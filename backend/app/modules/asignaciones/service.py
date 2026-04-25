from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException

from . import models, schema
from ..incidentes.models import Incidente


# ══════════════════════════════════════════════════
# HELPER — registrar cambio en historial_asignacion
# ══════════════════════════════════════════════════

def _registrar_historial(
    db: Session,
    asignacion_id: UUID,
    estado_anterior: str,
    estado_nuevo: str,
    cambiado_por: UUID = None,
    fuente: str = "tecnico",
    nota: str = None,
):
    registro = models.HistorialAsignacion(
        asignacion_id   = asignacion_id,
        estado_anterior = estado_anterior,
        estado_nuevo    = estado_nuevo,
        cambiado_por    = cambiado_por,
        fuente          = fuente,
        nota            = nota,
    )
    db.add(registro)


# ══════════════════════════════════════════════════
# CASOS DISPONIBLES (propuesta, sin técnico)
# ══════════════════════════════════════════════════

def get_casos_disponibles(db: Session, taller_id: UUID):
    from ..vehiculos.models import Vehiculo

    rows = (
        db.query(models.Asignacion, Incidente, Vehiculo)
        .join(Incidente, Incidente.id == models.Asignacion.incidente_id)
        .join(Vehiculo,  Vehiculo.id  == Incidente.vehiculo_id)
        .filter(
            and_(
                models.Asignacion.taller_id  == taller_id,
                models.Asignacion.estado     == "propuesta",
                models.Asignacion.usuario_id == None,
            )
        )
        .all()
    )

    resultado = []
    for asig, inc, veh in rows:
        resultado.append(schema.AsignacionOut(
            asignacion_id       = asig.id,
            incidente_id        = asig.incidente_id,
            estado              = asig.estado,
            distancia_km        = float(asig.distancia_km) if asig.distancia_km else None,
            tiempo_estimado_min = asig.tiempo_estimado_min,
            precio_cotizado     = float(asig.precio_cotizado) if asig.precio_cotizado else None,
            nota_taller         = asig.nota_taller,
            created_at          = asig.created_at,
            descripcion_manual  = inc.descripcion_manual,
            direccion_texto     = inc.direccion_texto,
            categoria           = inc.categoria,
            prioridad           = inc.prioridad,
            placa               = veh.placa,
            marca_vehiculo      = veh.marca,
            modelo_vehiculo     = veh.modelo,
            color_vehiculo      = veh.color,
        ))
    return resultado


# ══════════════════════════════════════════════════
# ACEPTAR CASO
# ══════════════════════════════════════════════════

def aceptar_caso(db: Session, asignacion_id: UUID, tecnico_usuario_id: UUID):
    asignacion = db.query(models.Asignacion).filter(
        models.Asignacion.id     == asignacion_id,
        models.Asignacion.estado == "propuesta"
    ).first()

    if not asignacion:
        return None  # ya fue tomado

    estado_anterior      = asignacion.estado
    asignacion.estado    = "aceptada"
    asignacion.usuario_id = tecnico_usuario_id
    asignacion.aceptado_at = datetime.utcnow()

    # Registrar en historial
    _registrar_historial(
        db             = db,
        asignacion_id  = asignacion.id,
        estado_anterior= estado_anterior,
        estado_nuevo   = "aceptada",
        cambiado_por   = tecnico_usuario_id,
        fuente         = "tecnico",
        nota           = "Caso aceptado por el técnico",
    )

    db.commit()
    db.refresh(asignacion)
    return asignacion


# ══════════════════════════════════════════════════
# HISTORIAL DEL TÉCNICO (con filtro por estado)
# ══════════════════════════════════════════════════

def get_historial_tecnico(
    db: Session,
    tecnico_usuario_id: UUID,
    estado: str = None,
):
    from ..vehiculos.models import Vehiculo

    query = (
        db.query(models.Asignacion, Incidente, Vehiculo)
        .join(Incidente, Incidente.id == models.Asignacion.incidente_id)
        .join(Vehiculo,  Vehiculo.id  == Incidente.vehiculo_id)
        .filter(models.Asignacion.usuario_id == tecnico_usuario_id)
    )

    # Filtro por categoría de estado
    if estado == "pendientes":
        query = query.filter(models.Asignacion.estado == "aceptada")
    elif estado == "proceso":
        query = query.filter(models.Asignacion.estado == "en_camino")
    elif estado == "terminados":
        query = query.filter(
            models.Asignacion.estado.in_(["completada", "cancelada"])
        )

    rows = query.order_by(models.Asignacion.created_at.desc()).all()

    resultado = []
    for asig, inc, veh in rows:
        resultado.append(schema.CasoHistorialOut(
            asignacion_id      = asig.id,
            incidente_id       = asig.incidente_id,
            estado             = asig.estado,
            categoria          = inc.categoria,
            prioridad          = inc.prioridad,
            descripcion_manual = inc.descripcion_manual,
            direccion_texto    = inc.direccion_texto,
            distancia_km       = float(asig.distancia_km) if asig.distancia_km else None,
            precio_cotizado    = float(asig.precio_cotizado) if asig.precio_cotizado else None,
            foto_evidencia     = inc.foto_evidencia,
            aceptado_at        = asig.aceptado_at,
            completado_at      = asig.completado_at,
            created_at         = asig.created_at,
            resumen_ia        = inc.resumen_ia,        # ← agrega
            confianza_ia      = float(inc.confianza_ia) if inc.confianza_ia else None,  # ← agrega
            requiere_revision = inc.requiere_revision, # ← agrega
            vehiculo = schema.VehiculoResumen(
                placa  = veh.placa,
                marca  = veh.marca,
                modelo = veh.modelo,
                color  = veh.color,
            ) if veh else None,
        ))
    return resultado


# ══════════════════════════════════════════════════
# CAMBIAR ESTADO DE UNA ASIGNACIÓN
# ══════════════════════════════════════════════════

TRANSICIONES_VALIDAS = {
    "aceptada":   ["en_camino", "cancelada"],
    "en_camino":  ["completada", "cancelada"],
}


def cambiar_estado(db, asignacion_id, nuevo_estado, tecnico_usuario_id, nota=None):
    asignacion = db.query(models.Asignacion).filter(
        models.Asignacion.id         == asignacion_id,
        models.Asignacion.usuario_id == tecnico_usuario_id,
    ).first()

    if not asignacion:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")

    estados_permitidos = TRANSICIONES_VALIDAS.get(asignacion.estado, [])
    if nuevo_estado not in estados_permitidos:
        raise HTTPException(
            status_code=400,
            detail=f"No puedes pasar de '{asignacion.estado}' a '{nuevo_estado}'"
        )

    estado_anterior   = asignacion.estado
    asignacion.estado = nuevo_estado

    if nuevo_estado == "en_camino":
        asignacion.iniciado_at = datetime.utcnow()
    elif nuevo_estado == "completada":
        asignacion.completado_at = datetime.utcnow()
    elif nuevo_estado == "cancelada":
        # ← DEVUELVE EL CASO: lo resetea a propuesta sin técnico
        asignacion.estado     = "propuesta"
        asignacion.usuario_id = None
        asignacion.aceptado_at = None
        asignacion.iniciado_at = None
        nuevo_estado = "propuesta"  # para el historial

    _registrar_historial(
        db              = db,
        asignacion_id   = asignacion.id,
        estado_anterior = estado_anterior,
        estado_nuevo    = nuevo_estado,
        cambiado_por    = tecnico_usuario_id,
        fuente          = "tecnico",
        nota            = nota,
    )

    db.commit()
    db.refresh(asignacion)
    return asignacion

