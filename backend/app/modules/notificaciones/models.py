import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.sql import func
from app.database import Base

class Notificacion(Base):
    __tablename__ = "notificaciones"

    id                = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    destinatario_id   = Column(UNIQUEIDENTIFIER, nullable=False)   # usuario_id del cliente
    tipo_destinatario = Column(String(20),  nullable=False, default="cliente")
    titulo            = Column(String(200), nullable=False)
    cuerpo            = Column(Text,        nullable=True)
    datos_extra       = Column(Text,        nullable=True)         # JSON como texto
    leida             = Column(Boolean,     nullable=False, default=False)
    created_at        = Column(DateTime,    nullable=False, server_default=func.now())