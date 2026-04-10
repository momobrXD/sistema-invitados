from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from models import get_db, Invitado, Asistencia, Evento
from auth import get_current_user

router = APIRouter(prefix="/api/personas", tags=["personas"])


class PersonaCreate(BaseModel):
    nombre: str
    cedula: str = ""
    estado: str = ""
    genero: str = ""
    correo: str = ""
    celular: str = ""
    cumple: str = ""
    zona: str = ""
    equipo: str = ""
    talento: str = ""
    observaciones: str = ""
    evento_actual: Optional[str] = None


class PersonaUpdate(BaseModel):
    nombre: Optional[str] = None
    cedula: Optional[str] = None
    estado: Optional[str] = None
    genero: Optional[str] = None
    correo: Optional[str] = None
    celular: Optional[str] = None
    cumple: Optional[str] = None
    zona: Optional[str] = None
    equipo: Optional[str] = None
    talento: Optional[str] = None
    observaciones: Optional[str] = None


def _inv_to_dict(inv: Invitado) -> dict:
    return {
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
    }


@router.get("/")
def listar_personas(db: Session = Depends(get_db), _user: str = Depends(get_current_user)):
    personas = db.query(Invitado).order_by(Invitado.nombre.asc()).all()
    return [_inv_to_dict(p) for p in personas]


@router.get("/cumpleaneros/mes")
def cumpleaneros_mes(db: Session = Depends(get_db), _user: str = Depends(get_current_user)):
    from utils import procesar_fecha, MESES_ES

    personas = db.query(Invitado).order_by(Invitado.nombre.asc()).all()
    mes_actual = datetime.now().month

    cumpleaneros = []
    for p in personas:
        mes, dia = procesar_fecha(p.cumple or "")
        if mes == mes_actual:
            cumpleaneros.append({
                **_inv_to_dict(p),
                "dia_orden": dia,
            })

    cumpleaneros.sort(key=lambda x: x.get("dia_orden", 99))

    return {
        "mes_nombre": MESES_ES[mes_actual],
        "mes": mes_actual,
        "cumpleaneros": cumpleaneros,
        "total": len(cumpleaneros),
    }


@router.get("/{id_inv}")
def get_persona(id_inv: int, db: Session = Depends(get_db), _user: str = Depends(get_current_user)):
    persona = db.query(Invitado).get(id_inv)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    return _inv_to_dict(persona)


@router.post("/")
def agregar_persona(body: PersonaCreate, db: Session = Depends(get_db), _user: str = Depends(get_current_user)):
    nuevo = Invitado(
        estado=body.estado,
        nombre=(body.nombre or "").upper(),
        genero=body.genero,
        cedula=body.cedula,
        correo=body.correo,
        celular=body.celular,
        cumple=body.cumple,
        zona=body.zona,
        equipo=body.equipo,
        talento=body.talento,
        observaciones=body.observaciones,
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return {"status": "ok", "id": nuevo.id, "mensaje": f"Invitado {nuevo.nombre} agregado"}


@router.put("/{id_inv}")
def editar_persona(id_inv: int, body: PersonaUpdate, db: Session = Depends(get_db), _user: str = Depends(get_current_user)):
    persona = db.query(Invitado).get(id_inv)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")

    if body.nombre is not None:
        persona.nombre = body.nombre.upper()
    if body.estado is not None:
        persona.estado = body.estado
    if body.genero is not None:
        persona.genero = body.genero
    if body.cedula is not None:
        persona.cedula = body.cedula
    if body.correo is not None:
        persona.correo = body.correo
    if body.celular is not None:
        persona.celular = body.celular
    if body.cumple is not None:
        persona.cumple = body.cumple
    if body.zona is not None:
        persona.zona = body.zona
    if body.equipo is not None:
        persona.equipo = body.equipo
    if body.talento is not None:
        persona.talento = body.talento
    if body.observaciones is not None:
        persona.observaciones = body.observaciones

    db.commit()
    return {"status": "ok", "mensaje": "Datos actualizados"}


@router.get("/{id_inv}/historial")
def historial_personal(id_inv: int, db: Session = Depends(get_db), _user: str = Depends(get_current_user)):
    persona = db.query(Invitado).get(id_inv)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")

    participaciones = (
        db.query(Asistencia, Evento)
        .join(Evento, Evento.id == Asistencia.evento_id)
        .filter(Asistencia.invitado_id == id_inv)
        .order_by(Asistencia.fecha.desc())
        .all()
    )

    return {
        "persona": _inv_to_dict(persona),
        "historial": [
            {
                "fecha": a.fecha.strftime("%d/%m/%Y") if a.fecha else "",
                "evento": ev.nombre_evento,
                "tipo_evento": ev.tipo_evento or "",
            }
            for a, ev in participaciones
        ],
    }
