"""
Importa datos desde CSV a PostgreSQL.
Coloca maestro.csv, eventos_creados.csv y eventos_log.csv en la carpeta scripts/
antes de ejecutar este script.
"""
import os
import sys
import csv
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import app, db, Evento, Invitado, Asistencia  # noqa: E402

SCRIPTS_DIR = Path(__file__).resolve().parent


def _read_csv(filename):
    path = SCRIPTS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"No se encontró {path}. Descárgalo desde Google Sheets.")
    with open(path, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def _parse_fecha(value):
    if not value:
        return None
    v = str(value).strip()
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(v, fmt).date()
        except ValueError:
            pass
    return None


def import_maestro(records):
    created = updated = 0
    for r in records:
        nro = str(r.get("Nro", "")).strip()
        if not nro.isdigit():
            continue
        inv_id = int(nro)
        nombre = (r.get("NOMBRE Y APELLIDO", "") or "").strip().upper()
        if not nombre:
            continue

        inv = db.session.get(Invitado, inv_id)
        if not inv:
            inv = Invitado(id=inv_id, nombre=nombre)
            db.session.add(inv)
            created += 1
        else:
            inv.nombre = nombre
            updated += 1

        inv.estado       = (r.get("ESTADO", "") or "").strip()
        inv.genero       = (r.get("GENERO", "") or "").strip()
        inv.cedula       = (r.get("CEDULA", "") or "").strip()
        inv.correo       = (r.get("CORREO", "") or "").strip()
        inv.celular      = (r.get("CELULAR", "") or "").strip()
        inv.cumple       = (r.get("CUMPLE", "") or "").strip()
        inv.zona         = (r.get("ZONA", "") or "").strip()
        inv.equipo       = (r.get("EQUIPO RECTOR", "") or r.get("EQUIPO", "") or "").strip()
        inv.talento      = (r.get("TALENTO", "") or "").strip()
        inv.observaciones = (r.get("OBSERVACIONES", "") or r.get("Observaciones", "") or "").strip()

    db.session.commit()
    return created, updated


def import_eventos(records):
    created = updated = 0
    for r in records:
        nombre = (r.get("Nombre_Evento", "") or "").strip()
        if not nombre:
            continue

        ev = Evento.query.filter_by(nombre_evento=nombre).first()
        if not ev:
            ev = Evento(nombre_evento=nombre)
            db.session.add(ev)
            created += 1
        else:
            updated += 1

        ev.tipo_evento  = (r.get("Tipo", "") or r.get("Tipo_Evento", "") or "OTRO").strip() or "OTRO"
        ev.fecha_evento = _parse_fecha(r.get("Fecha", "") or r.get("Fecha_Evento", ""))
        ev.estado       = (r.get("Estado", "") or "Abierto").strip() or "Abierto"

    db.session.commit()
    return created, updated


def import_logs(records):
    created = skipped = 0
    eventos = {e.nombre_evento: e.id for e in Evento.query.all()}

    for r in records:
        ev_nombre = (r.get("Evento_Especifico", "") or "").strip()
        if not ev_nombre:
            skipped += 1
            continue

        inv_id_raw = str(r.get("ID_Invitado", "")).strip()
        if not inv_id_raw.isdigit():
            skipped += 1
            continue
        inv_id = int(inv_id_raw)

        # Verificar que el invitado existe
        if not db.session.get(Invitado, inv_id):
            skipped += 1
            continue

        # Crear evento si no existe
        if ev_nombre not in eventos:
            ev = Evento(
                nombre_evento=ev_nombre,
                tipo_evento=(r.get("Tipo_Evento", "") or "OTRO").strip() or "OTRO",
                fecha_evento=_parse_fecha(r.get("Fecha", "")),
                estado="Cerrado"
            )
            db.session.add(ev)
            db.session.commit()
            eventos[ev_nombre] = ev.id

        evento_id = eventos[ev_nombre]
        fecha = _parse_fecha(r.get("Fecha", "")) or datetime.now().date()

        # Evitar duplicados
        existe = Asistencia.query.filter_by(
            evento_id=evento_id, invitado_id=inv_id
        ).first()
        if existe:
            skipped += 1
            continue

        db.session.add(Asistencia(evento_id=evento_id, invitado_id=inv_id, fecha=fecha))
        created += 1

        if (created + skipped) % 200 == 0:
            db.session.commit()
            print(f"  ... {created} asistencias importadas hasta ahora")

    db.session.commit()
    return created, skipped


def main():
    print("Leyendo CSVs...")
    maestro  = _read_csv("maestro.csv")
    eventos  = _read_csv("eventos_creados.csv")
    logs     = _read_csv("eventos_log.csv")
    print(f"  Maestro:  {len(maestro)} filas")
    print(f"  Eventos:  {len(eventos)} filas")
    print(f"  Log:      {len(logs)} filas")

    with app.app_context():
        db.create_all()

        print("\nImportando invitados...")
        c_i, u_i = import_maestro(maestro)
        print(f"  {c_i} creados, {u_i} actualizados")

        print("Importando eventos...")
        c_e, u_e = import_eventos(eventos)
        print(f"  {c_e} creados, {u_e} actualizados")

        print("Importando asistencias...")
        c_l, s_l = import_logs(logs)
        print(f"  {c_l} creadas, {s_l} saltadas")

    print("\n✅ Importación completa")
    print(f"   Invitados: {c_i} creados, {u_i} actualizados")
    print(f"   Eventos:   {c_e} creados, {u_e} actualizados")
    print(f"   Logs:      {c_l} asistencias creadas, {s_l} saltadas")


if __name__ == "__main__":
    main()
