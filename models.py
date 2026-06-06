from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database import Base

class TipoDocumento(str, enum.Enum):
    oficio = "oficio"
    resolucion = "resolucion"

class DocumentoMaestro(Base):
    __tablename__ = "documento_maestro"

    id = Column(Integer, primary_key=True, index=True)
    codigo_unico = Column(String(50), unique=True, index=True, nullable=False)
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    tipo_documento = Column(Enum(TipoDocumento), nullable=False)
    estado = Column(String(20), default="generado") # ej. "generado", "extraido", "firmado"
    ruta_pdf_final = Column(String(255), nullable=True)

    # Relaciones One-to-One
    # uselist=False asegura que sea una relación 1 a 1 en SQLAlchemy
    campos_oficio = relationship("CamposOficio", back_populates="maestro", uselist=False, cascade="all, delete-orphan")
    campos_resolucion = relationship("CamposResolucion", back_populates="maestro", uselist=False, cascade="all, delete-orphan")

class CamposOficio(Base):
    __tablename__ = "campos_oficio"

    id = Column(Integer, primary_key=True, index=True)
    maestro_id = Column(Integer, ForeignKey("documento_maestro.id"), unique=True, nullable=False)
    
    lema_anio = Column(String(255), nullable=True)
    lugar_fecha = Column(String(100), nullable=True)
    nro_oficio = Column(String(100), nullable=False)
    destinatario_titulo = Column(String(100), nullable=True)
    destinatario_nombre = Column(String(200), nullable=True)
    destinatario_cargo = Column(String(200), nullable=True)
    destinatario_dependencia = Column(String(200), nullable=True)
    asunto = Column(String(255), nullable=False)
    referencia = Column(Text, nullable=True)
    cuerpo_mensaje = Column(Text, nullable=False)
    remitente_nombre = Column(String(200), nullable=False)
    nt = Column(String(100), nullable=True)
    folios = Column(String(50), nullable=True)
    copia = Column(String(200), nullable=True)

    # Relación inversa al maestro
    maestro = relationship("DocumentoMaestro", back_populates="campos_oficio")

class CamposResolucion(Base):
    __tablename__ = "campos_resolucion"

    id = Column(Integer, primary_key=True, index=True)
    maestro_id = Column(Integer, ForeignKey("documento_maestro.id"), unique=True, nullable=False)
    
    nro_resolucion = Column(String(50), nullable=False)
    autoridad = Column(String(200), nullable=False)
    considerandos = Column(Text, nullable=False)
    articulos = Column(Text, nullable=False)

    # Relación inversa al maestro
    maestro = relationship("DocumentoMaestro", back_populates="campos_resolucion")
