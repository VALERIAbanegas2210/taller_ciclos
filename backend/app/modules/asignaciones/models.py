from sqlalchemy import Column, String, ForeignKey, DECIMAL, Integer, DateTime
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.database import Base

class Asignacion(Base):
    __tablename__ = "asignaciones"

    id = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    incidente_id = Column(UNIQUEIDENTIFIER, ForeignKey("incidentes.id"), nullable=False)
    taller_id = Column(UNIQUEIDENTIFIER, ForeignKey("talleres.id"), nullable=False)
    tecnico_id = Column(UNIQUEIDENTIFIER, ForeignKey("usuarios.id"), nullable=True) # El técnico que irá físicamente
    
    estado = Column(String(15), default="propuesta") # propuesta, aceptada, en_camino, completada
    
    distancia_km = Column(DECIMAL(8, 2))
    tiempo_estimado_min = Column(Integer)
    precio_cotizado = Column(DECIMAL(10, 2))
    nota_taller = Column(String(1000))
    
    aceptado_at = Column(DateTime, nullable=True)
    iniciado_at = Column(DateTime, nullable=True)
    completado_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    incidente = relationship("Incidente")
    # taller = relationship("Taller")