from sqlalchemy import Column, String, ForeignKey, DECIMAL, Boolean, DateTime
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.database import Base
from sqlalchemy.sql import func



class Incidente(Base):
    __tablename__ = "incidentes"

    id = Column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UNIQUEIDENTIFIER, ForeignKey("usuarios.id"), nullable=False)
    vehiculo_id = Column(UNIQUEIDENTIFIER, ForeignKey("vehiculos.id"), nullable=False)
    


# Dentro de tu clase Incidente:


    # Geolocalización y dirección
    direccion_texto = Column(String(500))
    ubicacion = Column(String(100)) # Formato "lat,long"
    descripcion_manual = Column(String(1000))

    # Clasificación
    categoria = Column(String(30), default="incierto") # bateria, llanta, choque, etc.
    prioridad = Column(String(10), default="media")
    estado = Column(String(15), default="pendiente") # pendiente, en_proceso, atendido, cancelado

    # Resultados opcionales (IA o manual)
    resumen_ia = Column(String(1000), nullable=True)
    confianza_ia = Column(DECIMAL(5, 4), nullable=True)
    requiere_revision = Column(Boolean, default=False)
    
    
    created_at = Column(DateTime, server_default=func.now())

    # Relaciones
    usuario = relationship("Usuario", back_populates="incidentes")
    # Asegúrate de tener la relación inversa en el modelo de Vehiculo
    # vehiculo = relationship("Vehiculo")
    vehiculo = relationship("Vehiculo", back_populates="incidentes")