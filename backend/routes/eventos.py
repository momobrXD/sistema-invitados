from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, date as date_type
from typing import Optional

from models import get_db, Evento, Asistencia, Invitado
from auth import get_current_user

router = APIRouter(prefix="/api/eventos", tags=["eventos"])


# ── Schemas ──

class EventoCreate(BaseModel):
    nombre_evento: str
    tipo_evento: str = "OTRO"
    fecha_evento: Optional[str] = None


class EventoCerrar(BaseModel):
    nombre_evento: str
    observaciones: str = ""


class EventoOut(BaseModel):
    id: int
    nombre_evento: str
    tipo_evento: str
    fecha_evento: Optional[str]
    estado: str
    observaciones: Optional[str]

    class Config:
        from_attributes = True


# ── Helpers ──

def _evento_to_dict(ev: Evento) -> dict:
    return {
        "id": ev.id,
        "nombre_evento": ev.nombre_evento,
        "tipo_evento": ev.tipo_evento,
        "fecha_evento": ev.fecha_evento.strftime("%d/%m/%Y") if ev.fecha_evento else "",
        "estado": ev.estado,
        "observaciones": ev.observaciones or "",
    }


# ── Endpoints ──

@router.get("/abiertos")
def listar_abiertos(db: Session = Depends(get_db), _user: str = Depends(get_current_user)):
    eventos = db.query(Evento).filter(Evento.estado != "Cerrado").order_by(Evento.id.desc()).all()
    return [_evento_to_dict(e) for e in eventos]


@router.get("/cerrados")
def listar_cerrados(db: Session = Depends(get_db), _user: str = Depends(get_current_user)):
    eventos = db.query(Evento).filter_by(estado="Cerrado").order_by(Evento.id.desc()).all()
    return [_evento_to_dict(e) for e in eventos]


@router.post("/crear")
def crear_evento(body: EventoCreate, db: Session = Depends(get_db), _user: str = Depends(get_current_user)):
    fecha_dt = None
    if body.fecha_evento:
        try:
            fecha_dt = datetime.strptime(body.fecha_evento, "%Y-%m-%d").date()
        except ValueError:
            try:
                fecha_dt = datetime.strptime(body.fecha_evento, "%d/%m/%Y").date()
            except ValueError:
                fecha_dt = None
    if not fecha_dt:
        fecha_dt = datetime.now().date()

    ev = Evento(
        nombre_evento=body.nombre_evento,
        tipo_evento=body.tipo_evento or "OTRO",
        fecha_evento=fecha_dt,
        estado="Abierto",
    )
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return {"status": "ok", "id": ev.id, "mensaje": f"Evento {body.nombre_evento} creado"}


@router.post("/cerrar")
def cerrar_evento(body: EventoCerrar, db: Session = Depends(get_db), _user: str = Depends(get_current_user)):
    ev = db.query(Evento).filter_by(nombre_evento=body.nombre_evento).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    ev.estado = "Cerrado"
    if body.observaciones:
        ev.observaciones = body.observaciones
    db.commit()
    return {"status": "ok", "mensaje": f"Evento '{body.nombre_evento}' cerrado"}


@router.get("/detalle/{nombre_evento}")
def detalle_evento(nombre_evento: str, db: Session = Depends(get_db), _user: str = Depends(get_current_user)):
    from utils import procesar_fecha, MESES_ES

    ev = db.query(Evento).filter_by(nombre_evento=nombre_evento).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    asistencias = (
        db.query(Asistencia, Invitado)
        .join(Invitado, Invitado.id == Asistencia.invitado_id)
        .filter(Asistencia.evento_id == ev.id)
        .order_by(Asistencia.id.asc())
        .all()
    )

    mes_actual = datetime.now().month
    asistentes = []
    cumpleaneros = []

    for a, inv in asistencias:
        item = {
            "fecha": a.fecha.strftime("%d/%m/%Y") if a.fecha else "",
            "evento": ev.nombre_evento,
            "tipo_evento": ev.tipo_evento,
            "id_invitado": inv.id,
            "cedula": inv.cedula or "",
            "nombre": inv.nombre or "",
            "celular": inv.celular or "",
            "estado": inv.estado or "",
            "talento": inv.talento or "",
            "observaciones": inv.observaciones or "",
            "es_cumple": False,
        }
        mes, dia = procesar_fecha(inv.cumple or "")
        if mes == mes_actual:
            item["es_cumple"] = True
            item["dia_cumple"] = dia
            cumpleaneros.append(item)
        asistentes.append(item)

    return {
        "evento": _evento_to_dict(ev),
        "asistentes": asistentes,
        "cumpleaneros": cumpleaneros,
        "mes_nombre": MESES_ES[mes_actual],
        "total": len(asistentes),
    }


@router.get("/previa_cierre/{nombre_evento}")
def previa_cierre(nombre_evento: str, db: Session = Depends(get_db), _user: str = Depends(get_current_user)):
    from utils import procesar_fecha, MESES_ES

    ev = db.query(Evento).filter_by(nombre_evento=nombre_evento).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    asistencias = (
        db.query(Asistencia, Invitado)
        .join(Invitado, Invitado.id == Asistencia.invitado_id)
        .filter(Asistencia.evento_id == ev.id)
        .all()
    )

    mes_actual = datetime.now().month
    asistentes = []
    cumpleaneros = []

    for a, inv in asistencias:
        asistentes.append({
            "id_invitado": inv.id,
            "nombre": inv.nombre,
        })
        mes, dia = procesar_fecha(inv.cumple or "")
        if mes == mes_actual:
            cumpleaneros.append({
                "nombre": inv.nombre,
                "dia": dia,
                "cumple": inv.cumple or "",
            })

    cumpleaneros.sort(key=lambda x: x["dia"])

    return {
        "evento": _evento_to_dict(ev),
        "asistentes": asistentes,
        "cumpleaneros": cumpleaneros,
        "mes_nombre": MESES_ES[mes_actual],
        "total_asistentes": len(asistentes),
    }
