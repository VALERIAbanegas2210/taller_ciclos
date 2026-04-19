import uuid
from sqlalchemy import Column, String, Boolean, Text
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from app.database import Base
import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Usuario(Base):
    __tablename__ = "usuarios"

    id            = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    nombres       = Column(String(100), nullable=False)
    apellidos     = Column(String(100), nullable=False)
    email         = Column(String(150), nullable=False, unique=True, index=True)
    telefono      = Column(String(20), nullable=True)
    password_hash = Column(Text, nullable=False)
    tipo          = Column(String(10), nullable=False, default="cliente")  # cliente|admin|taller|tecnico
    activo        = Column(Boolean, nullable=False, default=True)
    foto_perfil_url = Column(Text, nullable=True)
    import uuid

    vehiculos = relationship("Vehiculo", back_populates="usuario", cascade="all, delete")
    incidentes = relationship("Incidente", back_populates="usuario")


