import uuid
from sqlalchemy import Column, String, Boolean, Text, ForeignKey
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.orm import relationship
from app.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id              = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    nombres         = Column(String(100), nullable=False)
    apellidos       = Column(String(100), nullable=False)
    email           = Column(String(150), nullable=False, unique=True, index=True)
    telefono        = Column(String(20),  nullable=True)
    password_hash   = Column(Text,        nullable=False)
    tipo            = Column(String(10),  nullable=False, default="cliente")  # cliente|admin|tecnico
    activo          = Column(Boolean,     nullable=False, default=True)
    foto_perfil_url = Column(Text,        nullable=True)

    # Solo aplica si tipo='tecnico' — indica a qué taller pertenece
    taller_id = Column(UNIQUEIDENTIFIER, ForeignKey("talleres.id"), nullable=True)

    # --- RELACIONES ---
    vehiculos              = relationship("Vehiculo",   back_populates="usuario", cascade="all, delete")
    incidentes             = relationship("Incidente",  back_populates="usuario")
    asignaciones_aceptadas = relationship("Asignacion", back_populates="tecnico")
    taller                 = relationship("Taller",     back_populates="tecnicos", foreign_keys=[taller_id])
