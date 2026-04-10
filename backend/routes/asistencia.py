from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from models import get_db, Evento, Asistencia, Invitado
from auth import get_current_user

router = APIRouter(prefix="/api/asistencia", tags=["asistencia"])


class AsistenciaMasiva(BaseModel):
    invitados_ids: list[int]
    accion: str  # "registrar" | "quitar"
    evento_nombre: str
    tipo_evento: str = "Reunión"


@router.get("/lista/{nombre_evento}")
def lista_asistencia(nombre_evento: str, db: Session = Depends(get_db), _user: str = Depends(get_current_user)):
    from utils import procesar_fecha, MESES_ES

    ev = db.query(Evento).filter_by(nombre_evento=nombre_evento).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    invitados = db.query(Invitado).order_by(Invitado.nombre.asc()).all()
    asistencias = db.query(Asistencia).filter_by(evento_id=ev.id).all()
    asistentes_ids = [a.invitado_id for a in asistencias]

    mes_actual = datetime.now().month
    cumpleaneros = []

    inv_list = []
    for inv in invitados:
        item = {
            "nro": inv.id,
            "estado": inv.estado or "",
            "nombre": inv.nombre or "",
            "genero": inv.genero or "",
            "cedula": inv.cedula or "",
            "correo": inv.correo or "",
            "celular": inv.celular or "",
            "cumple": inv.cumple or "",
            "zona": inv.zona or "",
            "equipo": inv.equipo or "",
            "talento": inv.talento or "",
            "observaciones": inv.observaciones or "",
            "presente": inv.id in asistentes_ids,
        }
        mes, dia = procesar_fecha(inv.cumple or "")
        if mes == mes_actual:
            item["dia_cumple"] = dia
            cumpleaneros.append(item)
        inv_list.append(item)

    return {
        "evento": {
            "id": ev.id,
            "nombre_evento": ev.nombre_evento,
            "tipo_evento": ev.tipo_evento,
            "fecha_evento": ev.fecha_evento.strftime("%d/%m/%Y") if ev.fecha_evento else "",
            "estado": ev.estado,
        },
        "invitados": inv_list,
        "asistentes_ids": asistentes_ids,
        "total_registrados": len(asistentes_ids),
        "total_invitados": len(inv_list),
        "cumpleaneros": cumpleaneros,
        "mes_nombre": MESES_ES[mes_actual],
    }


@router.post("/masiva")
def procesar_masiva(body: AsistenciaMasiva, db: Session = Depends(get_db), _user: str = Depends(get_current_user)):
    ev = db.query(Evento).filter_by(nombre_evento=body.evento_nombre).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    if body.accion == "registrar":
        hoy = datetime.now().date()
        for inv_id in body.invitados_ids:
            exists = db.query(Asistencia).filter_by(evento_id=ev.id, invitado_id=inv_id).first()
            if not exists:
                db.add(Asistencia(evento_id=ev.id, invitado_id=inv_id, fecha=hoy))
        db.commit()

    elif body.accion == "quitar":
        db.query(Asistencia).filter(
            Asistencia.evento_id == ev.id,
            Asistencia.invitado_id.in_(body.invitados_ids),
        ).delete(synchronize_session=False)
        db.commit()

    # Retornar conteo actualizado
    total = db.query(Asistencia).filter_by(evento_id=ev.id).count()
    return {"status": "ok", "total_registrados": total}


@router.get("/historial/{id_inv}")
def historial_usuario(id_inv: int, db: Session = Depends(get_db), _user: str = Depends(get_current_user)):
    asistencias = (
        db.query(Asistencia, Evento)
        .join(Evento, Evento.id == Asistencia.evento_id)
        .filter(Asistencia.invitado_id == id_inv)
        .order_by(Asistencia.fecha.desc())
        .all()
    )
    return [
        {
            "fecha": a.fecha.strftime("%d/%m/%Y") if a.fecha else "",
            "evento": ev.nombre_evento,
            "tipo_evento": ev.tipo_evento or "",
        }
        for a, ev in asistencias
    ]


@router.get("/reportes")
def reportes(db: Session = Depends(get_db), _user: str = Depends(get_current_user)):
    rows = (
        db.query(Asistencia, Evento, Invitado)
        .join(Evento, Evento.id == Asistencia.evento_id)
        .join(Invitado, Invitado.id == Asistencia.invitado_id)
        .order_by(Asistencia.fecha.desc(), Asistencia.id.desc())
        .all()
    )
    return [
        {
            "fecha": a.fecha.strftime("%d/%m/%Y") if a.fecha else "",
            "evento": ev.nombre_evento,
            "tipo_evento": ev.tipo_evento or "",
            "cedula": inv.cedula or "",
            "nombre": inv.nombre or "",
            "mes": a.fecha.strftime("%B") if a.fecha else "",
        }
        for a, ev, inv in rows
    ]
