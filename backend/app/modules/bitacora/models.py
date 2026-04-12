import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from app.database import Base

class Bitacora(Base):
    __tablename__ = "bitacora_sesiones"

    id          = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    usuario_id  = Column(UNIQUEIDENTIFIER, ForeignKey("usuarios.id"), nullable=False)
    email       = Column(String(150), nullable=False)
    nombres     = Column(String(200), nullable=False)
    tipo        = Column(String(20), nullable=False)   # admin | cliente | tecnico
    accion      = Column(String(20), nullable=False)   # login | logout
    fecha_hora  = Column(DateTime, default=datetime.utcnow, nullable=False)
    ip          = Column(String(50), nullable=True)