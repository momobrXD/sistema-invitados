from sqlalchemy import (
    Column, Integer, String, Text, Date, ForeignKey, UniqueConstraint, create_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import date as date_type

from config import DATABASE_URL

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Evento(Base):
    __tablename__ = "eventos"

    id = Column(Integer, primary_key=True, index=True)
    nombre_evento = Column(String(200), unique=True, nullable=False)
    tipo_evento = Column(String(60), nullable=False, default="OTRO")
    fecha_evento = Column(Date, nullable=True)
    estado = Column(String(20), nullable=False, default="Abierto")
    observaciones = Column(Text, nullable=True)


class Invitado(Base):
    __tablename__ = "invitados"

    id = Column(Integer, primary_key=True, index=True)
    estado = Column(String(60), nullable=True)
    nombre = Column(String(200), nullable=False)
    genero = Column(String(20), nullable=True)
    cedula = Column(String(40), nullable=True, index=True)
    correo = Column(String(200), nullable=True)
    celular = Column(String(40), nullable=True)
    cumple = Column(String(40), nullable=True)
    zona = Column(String(120), nullable=True)
    equipo = Column(String(120), nullable=True)
    talento = Column(Text, nullable=True)
    observaciones = Column(Text, nullable=True)


class Asistencia(Base):
    __tablename__ = "asistencias"

    id = Column(Integer, primary_key=True, index=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False, index=True)
    invitado_id = Column(Integer, ForeignKey("invitados.id"), nullable=False, index=True)
    fecha = Column(Date, nullable=False, default=date_type.today)

    __table_args__ = (
        UniqueConstraint("evento_id", "invitado_id", name="uq_asistencia_evento_invitado"),
    )
