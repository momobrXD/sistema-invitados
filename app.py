from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import gspread
from google.oauth2.service_account import Credentials
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_caching import Cache
from datetime import datetime
from datetime import date as date_type
import time
import os
import json
from functools import wraps

app = Flask(__name__)
app.secret_key = 'mcc_sistema_2026_pro_secure'

# ==========================================
# CONFIGURACIÓN DE CACHE
# ==========================================
cache = Cache(app, config={
    'CACHE_TYPE': 'SimpleCache',
    'CACHE_DEFAULT_TIMEOUT': 120,  # 2 minutos por defecto
})

# ==========================================
# CONFIGURACIÓN DE BASE DE DATOS (POSTGRES)
# ==========================================
def _normalize_database_url(url: str | None) -> str | None:
    if not url:
        return None
    # Render a veces entrega postgres:// y SQLAlchemy espera postgresql://
    if url.startswith("postgres://"):
        return "postgresql://" + url[len("postgres://") :]
    return url


db = SQLAlchemy()
migrate = Migrate()

db_uri = _normalize_database_url(os.environ.get("DATABASE_URL")) or "sqlite:///local.db"
app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
migrate.init_app(app, db)


class Evento(db.Model):
    __tablename__ = "eventos"

    id = db.Column(db.Integer, primary_key=True)
    nombre_evento = db.Column(db.String(200), unique=True, nullable=False)
    tipo_evento = db.Column(db.String(60), nullable=False, default="OTRO")
    fecha_evento = db.Column(db.Date, nullable=True)
    estado = db.Column(db.String(20), nullable=False, default="Abierto")  # Abierto|Cerrado
    observaciones = db.Column(db.Text, nullable=True)


class Invitado(db.Model):
    __tablename__ = "invitados"

    id = db.Column(db.Integer, primary_key=True)  # este será tu "Nro"
    estado = db.Column(db.String(60), nullable=True)
    nombre = db.Column(db.String(200), nullable=False)
    genero = db.Column(db.String(20), nullable=True)
    cedula = db.Column(db.String(40), nullable=True, index=True)
    correo = db.Column(db.String(200), nullable=True)
    celular = db.Column(db.String(40), nullable=True)
    cumple = db.Column(db.String(40), nullable=True)  # mantener texto por compatibilidad con tu parseador
    zona = db.Column(db.String(120), nullable=True)
    equipo = db.Column(db.String(120), nullable=True)
    talento = db.Column(db.Text, nullable=True)
    observaciones = db.Column(db.Text, nullable=True)


class Asistencia(db.Model):
    __tablename__ = "asistencias"

    id = db.Column(db.Integer, primary_key=True)
    evento_id = db.Column(db.Integer, db.ForeignKey("eventos.id"), nullable=False, index=True)
    invitado_id = db.Column(db.Integer, db.ForeignKey("invitados.id"), nullable=False, index=True)
    fecha = db.Column(db.Date, nullable=False, default=date_type.today)

    __table_args__ = (
        db.UniqueConstraint("evento_id", "invitado_id", name="uq_asistencia_evento_invitado"),
    )


def _evento_to_template_dict(ev: Evento) -> dict:
    fecha_str = ev.fecha_evento.strftime("%d/%m/%Y") if ev.fecha_evento else ""
    return {
        "Nombre_Evento": ev.nombre_evento,
        "Tipo": ev.tipo_evento,
        "Tipo_Evento": ev.tipo_evento,
        "Fecha": fecha_str,
        "Fecha_Evento": fecha_str,
        "Estado": ev.estado,
        "Observaciones": ev.observaciones or "",
    }


def _invitado_to_template_dict(inv: Invitado) -> dict:
    return {
        "Nro": inv.id,
        "ESTADO": inv.estado or "",
        "NOMBRE Y APELLIDO": inv.nombre or "",
        "GENERO": inv.genero or "",
        "CEDULA": inv.cedula or "",
        "CORREO": inv.correo or "",
        "CELULAR": inv.celular or "",
        "CUMPLE": inv.cumple or "",
        "ZONA": inv.zona or "",
        "EQUIPO": inv.equipo or "",
        "TALENTO": inv.talento or "",
        "OBSERVACIONES": inv.observaciones or "",
    }

# ==========================================
# CONFIGURACIÓN DE SEGURIDAD (LOGIN)
# ==========================================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' 

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# ==========================================
# DECORADOR PARA EVITAR ERROR 429 (CUOTA)
# ==========================================
def retry_on_429(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        for i in range(3):  # 3 intentos
            try:
                return f(*args, **kwargs)
            except Exception as e:
                if "429" in str(e) and i < 2:
                    time.sleep(2)  # Espera 2 segundos
                else:
                    raise e
    return wrapper

# ==========================================
# GESTOR DE BASE DE DATOS (GOOGLE SHEETS)
# ==========================================
class GSheetManager:
    def __init__(self):
        self.scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        # Carga de credenciales
        if os.path.exists('credenciales-google.json'):
            self.creds = Credentials.from_service_account_file('credenciales-google.json', scopes=self.scope)
        else:
            creds_info = json.loads(os.environ.get("GOOGLE_CREDENTIALS", "{}"))
            self.creds = Credentials.from_service_account_info(creds_info, scopes=self.scope)
            
        self.client = gspread.authorize(self.creds)
        
        # IMPORTANTE: Revisa si tu hoja se llama "BaseMCC" o "SISTEMA-INVITADOS"
        # Según tu código anterior era BaseMCC, pero tu foto decía SISTEMA-INVITADOS.
        # Pon aquí el nombre REAL que ves en Google Sheets.
        self.sh = self.client.open("BaseMCC") 
        
        self.ws_cache = {}
        self._load_sheets()

    @retry_on_429
    def _load_sheets(self):
        # Nombres exactos de tus pestañas
        nombres = ["Config", "Eventos_Creados", "Maestro", "Eventos_Log"]
        for n in nombres:
            try:
                self.ws_cache[n] = self.sh.worksheet(n)
            except gspread.WorksheetNotFound:
                print(f"Advertencia: No se encontró la hoja {n}")

    def get_ws(self, name):
        # Si por alguna razón se desconectó, intenta recargar
        if name not in self.ws_cache:
            self.ws_cache[name] = self.sh.worksheet(name)
        return self.ws_cache.get(name)

    @retry_on_429
    def get_batch_data(self, sheet_name):
        ws = self.get_ws(sheet_name)
        data = ws.get_all_values()
        if not data: return []
        headers = data[0]
        # Filtra filas vacías para evitar errores
        return [dict(zip(headers, row)) for row in data[1:] if row and row[0]]

class GSMProxy:
    """
    Inicializa Google Sheets de forma lazy para no bloquear el arranque
    (Render importa el módulo antes de tener todo listo).
    """
    def __init__(self):
        self._gsm = None

    def _get_gsm(self):
        if self._gsm is None:
            try:
                self._gsm = GSheetManager()
            except Exception as e:
                raise RuntimeError(f"No se pudo inicializar Google Sheets: {e}")
        return self._gsm

    def __getattr__(self, item):
        return getattr(self._get_gsm(), item)

# Mantener el mismo nombre para no tocar el resto del código.
gsm = GSMProxy()

def procesar_fecha(fecha_str):
    """Función global para convertir cualquier formato de fecha en mes y día numérico"""
    if not fecha_str: return None, 99
    fecha_str = str(fecha_str).strip().lower()
    
    meses_texto = {
        'ene': 1, 'enero': 1, 'feb': 2, 'febrero': 2, 'mar': 3, 'marzo': 3,
        'abr': 4, 'abril': 4, 'may': 5, 'mayo': 5, 'jun': 6, 'junio': 6,
        'jul': 7, 'julio': 7, 'ago': 8, 'agosto': 8, 'sep': 9, 'septiembre': 9,
        'oct': 10, 'octubre': 10, 'nov': 11, 'noviembre': 11, 'dic': 12, 'diciembre': 12
    }

    formatos = [
        '%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%Y/%m/%d', 
        '%d/%m', '%d-%m', '%m/%d/%Y', '%m-%d-%Y'
    ]
    
    for fmt in formatos:
        try:
            dt = datetime.strptime(fecha_str, fmt)
            return dt.month, dt.day
        except ValueError:
            continue
            
    try:
        partes = fecha_str.replace('-', '/').replace(' ', '/').split('/')
        if len(partes) >= 2:
            dia = int(partes[0])
            mes_str = partes[1]
            mes = meses_texto.get(mes_str, int(mes_str) if mes_str.isdigit() else None)
            if mes: return mes, dia
    except:
        pass 
        
    return None, 99

# ==========================================
# RUTAS DE AUTENTICACIÓN
# ==========================================


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('username')
        pw = request.form.get('password')
        if user == "admin" and pw == "mcc2026":
            login_user(User(user))
            return redirect(url_for('index'))
        flash("Usuario o clave incorrectos")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ==========================================
# RUTAS DEL PANEL PRINCIPAL
# ==========================================

@app.route('/')
@login_required
def index():
    try:
        tipos = []
        eventos_abiertos = (
            Evento.query.filter(Evento.estado != "Cerrado")
            .order_by(Evento.id.desc())
            .all()
        )
        abiertos = [_evento_to_template_dict(e) for e in eventos_abiertos]
        return render_template('index.html', tipos=tipos, eventos=abiertos)
    except Exception as e:
        return f"Error cargando el inicio: {str(e)}"

@app.route('/crear_evento', methods=['POST'])
@login_required
@retry_on_429
def crear_evento():
    nombre = request.form.get('nombre_evento') or request.form.get('nombre')
    tipo = request.form.get('tipo_evento') or request.form.get('tipo')
    fecha_input = request.form.get('fecha_evento') or request.form.get('fecha')
    
    # Formateo de fecha seguro
    if fecha_input:
        try:
            # Intenta convertir si viene en formato YYYY-MM-DD
            fecha_dt = datetime.strptime(fecha_input, '%Y-%m-%d')
            fecha_final = fecha_dt.strftime('%d/%m/%Y')
        except ValueError:
            fecha_final = fecha_input # Si ya viene bien, lo deja así
    else:
        fecha_final = datetime.now().strftime('%d/%m/%Y')

    # Guardar en Postgres
    fecha_dt = None
    if fecha_final:
        try:
            fecha_dt = datetime.strptime(fecha_final, "%d/%m/%Y").date()
        except ValueError:
            fecha_dt = None

    ev = Evento(
        nombre_evento=nombre,
        tipo_evento=tipo or "OTRO",
        fecha_evento=fecha_dt,
        estado="Abierto",
    )
    db.session.add(ev)
    db.session.commit()
    flash(f"Evento {nombre} creado correctamente")
    return redirect(url_for('index'))

# ==========================================
# RUTAS DE ASISTENCIA Y CONSULTA
# ==========================================

@app.route('/tomar_lista/<nombre_evento>')
@login_required
def tomar_lista(nombre_evento):
    ev = Evento.query.filter_by(nombre_evento=nombre_evento).first()
    if not ev:
        return f"Evento no encontrado: {nombre_evento}", 404
    evento_info = _evento_to_template_dict(ev)

    invitados_db = Invitado.query.order_by(Invitado.nombre.asc()).all()
    invitados = [_invitado_to_template_dict(i) for i in invitados_db]

    asistencias = Asistencia.query.filter_by(evento_id=ev.id).all()
    asistentes_ids = [str(a.invitado_id) for a in asistencias]
    
    mes_actual = datetime.now().month
    meses_es = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    
    cumpleañeros_del_evento = []
    for inv in invitados:
        # Ahora sí encontrará la función porque es global
        mes_cumple, dia_cumple = procesar_fecha(inv.get('CUMPLE', ''))
        if mes_cumple == mes_actual:
            inv['dia_cumple'] = dia_cumple
            cumpleañeros_del_evento.append(inv)
    
    return render_template('lista.html', 
                           invitados=invitados, 
                           evento=evento_info, 
                           asistentes_ids=asistentes_ids,
                           cumpleañeros=cumpleañeros_del_evento,
                           mes_nombre=meses_es[mes_actual])


@app.route('/procesar_asistencia_masiva', methods=['POST'])
@login_required
@retry_on_429
def procesar_asistencia_masiva():
    ids_sel = request.form.getlist('invitados_ids')
    accion = request.form.get('accion')
    ev_nombre = request.form.get('evento_nombre')
    ev_tipo = request.form.get('tipo_evento') or "Reunión"

    ev = Evento.query.filter_by(nombre_evento=ev_nombre).first()
    if not ev:
        return jsonify({"status": "error", "message": "Evento no encontrado"}), 404
    if ev_tipo and (not ev.tipo_evento):
        ev.tipo_evento = ev_tipo

    ids_int = []
    for x in ids_sel:
        try:
            ids_int.append(int(x))
        except ValueError:
            continue

    if accion == 'registrar':
        hoy = datetime.now().date()
        for inv_id in ids_int:
            a = Asistencia(evento_id=ev.id, invitado_id=inv_id, fecha=hoy)
            db.session.add(a)
        try:
            db.session.commit()
        except Exception:
            # por el unique constraint, si ya existe una asistencia, hacemos rollback y seguimos
            db.session.rollback()
            for inv_id in ids_int:
                exists = Asistencia.query.filter_by(evento_id=ev.id, invitado_id=inv_id).first()
                if not exists:
                    db.session.add(Asistencia(evento_id=ev.id, invitado_id=inv_id, fecha=hoy))
            db.session.commit()

    elif accion == 'quitar':
        Asistencia.query.filter(
            Asistencia.evento_id == ev.id,
            Asistencia.invitado_id.in_(ids_int),
        ).delete(synchronize_session=False)
        db.session.commit()

    # Invalidar caches que dependen de asistencia
    cache.delete('reportes')
    cache.delete('consultas')

    return jsonify({"status": "ok"})

# --- RUTAS DE HISTORIAL QUE YA TENÍAS ---

@app.route('/historial_usuario/<id_inv>')
@login_required
@cache.cached(timeout=180)  # 3 min
def historial_usuario(id_inv):
    try:
        inv_id = int(id_inv)
    except ValueError:
        return jsonify([])

    asistencias = (
        db.session.query(Asistencia, Evento)
        .join(Evento, Evento.id == Asistencia.evento_id)
        .filter(Asistencia.invitado_id == inv_id)
        .order_by(Asistencia.fecha.desc())
        .all()
    )
    out = []
    for a, ev in asistencias:
        out.append(
            {
                "Fecha": a.fecha.strftime("%d/%m/%Y") if a.fecha else "",
                "Evento": ev.nombre_evento,
            }
        )
    return jsonify(out)

@app.route('/cumpleañeros')
@login_required
@cache.cached(timeout=1800, key_prefix='cumpleaneros')  # 30 min — cambia 1 vez al mes
def cumpleañeros():
    """Muestra todas las personas que tienen cumpleaños en el mes actual"""
    personas_db = Invitado.query.order_by(Invitado.nombre.asc()).all()
    personas = [_invitado_to_template_dict(p) for p in personas_db]
    mes_actual = datetime.now().month
    
    meses_es = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    mes_nombre = meses_es[mes_actual]

    cumpleañeros_mes = []
    for p in personas:
        # Usa la función global definida arriba
        mes_cumple, dia_cumple = procesar_fecha(p.get('CUMPLE', ''))
        
        if mes_cumple == mes_actual:
            p['dia_orden'] = dia_cumple
            cumpleañeros_mes.append(p)
    
    cumpleañeros_mes.sort(key=lambda p: p.get('dia_orden', 99))
    
    return render_template('cumpleañeros.html', 
                           mes_nombre=mes_nombre,
                           mes=mes_actual,
                           cumpleañeros=cumpleañeros_mes,
                           total=len(cumpleañeros_mes))

@app.route('/consultas')
@login_required
@cache.cached(timeout=300, key_prefix='consultas')  # 5 min — solo cambia al cerrar evento
def consultas():
    eventos_db = (
        Evento.query.filter_by(estado="Cerrado")
        .order_by(Evento.id.desc())
        .all()
    )
    cerrados = [_evento_to_template_dict(e) for e in eventos_db]
    personas_db = Invitado.query.order_by(Invitado.nombre.asc()).all()
    personas = [_invitado_to_template_dict(p) for p in personas_db]
    return render_template('consultas.html', eventos=cerrados, personas=personas)


@app.route('/reportes')
@login_required
@cache.cached(timeout=300, key_prefix='reportes')  # 5 min
def reportes():
    """Reporte global de todas las asistencias."""
    rows = (
        db.session.query(Asistencia, Evento, Invitado)
        .join(Evento, Evento.id == Asistencia.evento_id)
        .join(Invitado, Invitado.id == Asistencia.invitado_id)
        .order_by(Asistencia.fecha.desc(), Asistencia.id.desc())
        .all()
    )
    asistencias = []
    for a, ev, inv in rows:
        asistencias.append({
            "Fecha": a.fecha.strftime("%d/%m/%Y") if a.fecha else "",
            "Evento_Especifico": ev.nombre_evento,
            "Tipo_Evento": ev.tipo_evento or "—",
            "Cedula_Invitado": inv.cedula or "",
            "Nombre_Invitado": inv.nombre or "",
            "Mes": a.fecha.strftime("%B") if a.fecha else "",
        })
    return render_template("reportes.html", asistencias=asistencias)


@app.route('/detalle_evento_cerrado/<nombre_evento>')
@login_required
@retry_on_429
@cache.cached(timeout=3600)  # 1 hora — evento cerrado no cambia
def detalle_evento_cerrado(nombre_evento):
    ev = Evento.query.filter_by(nombre_evento=nombre_evento).first()
    if not ev:
        return f"Evento no encontrado: {nombre_evento}", 404

    asistencias = (
        db.session.query(Asistencia, Invitado)
        .join(Invitado, Invitado.id == Asistencia.invitado_id)
        .filter(Asistencia.evento_id == ev.id)
        .order_by(Asistencia.id.asc())
        .all()
    )
    asistentes = []
    for a, inv in asistencias:
        asistentes.append(
            {
                "Fecha": a.fecha.strftime("%d/%m/%Y") if a.fecha else "",
                "Evento_Especifico": ev.nombre_evento,
                "Tipo_Evento": ev.tipo_evento,
                "ID_Invitado": inv.id,
                "Cedula": inv.cedula or "",
                "Nombre_Invitado": inv.nombre or "",
                "Mes": a.fecha.strftime("%B") if a.fecha else "",
            }
        )
    
    mes_actual = datetime.now().month
    meses_es = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    
    cumpleañeros_asistentes = []
    for asis in asistentes:
        persona = Invitado.query.get(int(asis.get("ID_Invitado")))
        
        # Enriquecer con datos del Maestro
        asis['Celular']       = (persona.celular if persona else "") or ""
        asis['Estado']        = (persona.estado if persona else "") or ""
        asis['Talento']       = (persona.talento if persona else "") or ""
        asis['Observaciones'] = (persona.observaciones if persona else "") or ""
        asis['es_cumple']     = False

        # Detectar cumpleañeros
        mes, dia = procesar_fecha((persona.cumple if persona else "") or "")
        if mes == mes_actual:
            asis['es_cumple']  = True
            asis['dia_cumple'] = dia
            cumpleañeros_asistentes.append(asis)

    return render_template('detalle_historial.html', 
                           nombre=nombre_evento, 
                           lista=asistentes, 
                           tipo="evento",
                           cumpleañeros=cumpleañeros_asistentes,
                           mes_nombre=meses_es[mes_actual])

@app.route('/historial_personal/<id_inv>')
@login_required
@retry_on_429
@cache.cached(timeout=180)  # 3 min
def historial_personal(id_inv):
    try:
        inv_id = int(id_inv)
    except ValueError:
        return "ID inválido", 400

    persona_db = Invitado.query.get(inv_id)
    if not persona_db:
        return "Persona no encontrada", 404

    persona = _invitado_to_template_dict(persona_db)
    participaciones = (
        db.session.query(Asistencia, Evento)
        .join(Evento, Evento.id == Asistencia.evento_id)
        .filter(Asistencia.invitado_id == inv_id)
        .order_by(Asistencia.fecha.desc())
        .all()
    )
    lista = []
    for a, ev in participaciones:
        lista.append(
            {
                "Fecha": a.fecha.strftime("%d/%m/%Y") if a.fecha else "",
                "Evento_Especifico": ev.nombre_evento,
                "Tipo_Evento": ev.tipo_evento,
                "ID_Invitado": inv_id,
                "Nombre_Invitado": persona_db.nombre,
            }
        )
    return render_template('detalle_historial.html', persona=persona, lista=lista, tipo="persona")

@app.route('/previa_cierre/<nombre_evento>')
@login_required
def previa_cierre(nombre_evento):
    """Vista previa antes de cerrar un evento: cumpleañeros y observaciones"""
    ev = Evento.query.filter_by(nombre_evento=nombre_evento).first()
    if not ev:
        return f"Evento no encontrado: {nombre_evento}", 404
    evento_info = _evento_to_template_dict(ev)

    asistencias = (
        db.session.query(Asistencia, Invitado)
        .join(Invitado, Invitado.id == Asistencia.invitado_id)
        .filter(Asistencia.evento_id == ev.id)
        .all()
    )
    asistentes = []
    for a, inv in asistencias:
        asistentes.append(
            {
                "Fecha": a.fecha.strftime("%d/%m/%Y") if a.fecha else "",
                "Evento_Especifico": ev.nombre_evento,
                "Tipo_Evento": ev.tipo_evento,
                "ID_Invitado": inv.id,
                "Nombre_Invitado": inv.nombre,
            }
        )

    mes_actual = datetime.now().month
    meses_es = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

    cumpleañeros_evento = []
    for asis in asistentes:
        persona = Invitado.query.get(int(asis.get("ID_Invitado")))
        mes, dia = procesar_fecha((persona.cumple if persona else "") or "")
        if mes == mes_actual:
            cumpleañeros_evento.append({
                'nombre': asis.get('Nombre_Invitado', 'N/A'),
                'dia': dia,
                'cumple': (persona.cumple if persona else "") or ""
            })
    cumpleañeros_evento.sort(key=lambda x: x['dia'])

    return render_template('previa_cierre.html',
                           evento=evento_info,
                           nombre_evento=nombre_evento,
                           asistentes=asistentes,
                           cumpleañeros=cumpleañeros_evento,
                           mes_nombre=meses_es[mes_actual],
                           total_asistentes=len(asistentes))

@app.route('/cerrar_evento', methods=['POST'])
@login_required
@retry_on_429
def cerrar_evento():
    nombre = request.form.get('nombre_evento')
    observaciones = request.form.get('observaciones', '')
    ev = Evento.query.filter_by(nombre_evento=nombre).first()
    if ev:
        ev.estado = "Cerrado"
        if observaciones:
            ev.observaciones = observaciones
        db.session.commit()
    # Invalidar caches afectados por cierre de evento
    cache.delete('consultas')
    cache.delete('reportes')
    flash(f"Evento '{nombre}' cerrado correctamente.")
    return redirect(url_for('index'))

@app.route('/get_persona/<id_inv>')
@login_required
def get_persona(id_inv):
    """API para obtener datos completos de una persona para editar"""
    try:
        inv_id = int(id_inv)
    except ValueError:
        return jsonify({"error": "ID inválido"}), 400
    persona_db = Invitado.query.get(inv_id)
    if not persona_db:
        return jsonify({"error": "No encontrado"}), 404
    return jsonify(_invitado_to_template_dict(persona_db))

@app.route('/editar_persona/<id_inv>', methods=['POST'])
@login_required
@retry_on_429
def editar_persona(id_inv):
    """Edita los datos de una persona en la hoja Maestro"""
    try:
        inv_id = int(id_inv)
    except ValueError:
        return jsonify({"error": "ID inválido"}), 400

    persona = Invitado.query.get(inv_id)
    if not persona:
        return jsonify({"error": "Persona no encontrada"}), 404

    # Acepta el mismo payload que el frontend/tu JS actual
    persona.estado = request.form.get("ESTADO", persona.estado or "")
    nombre = request.form.get("NOMBRE Y APELLIDO", persona.nombre or "")
    persona.nombre = (nombre or "").upper()
    persona.genero = request.form.get("GENERO", persona.genero or "")
    persona.cedula = request.form.get("CEDULA", persona.cedula or "")
    persona.correo = request.form.get("CORREO", persona.correo or "")
    persona.celular = request.form.get("CELULAR", persona.celular or "")
    persona.cumple = request.form.get("CUMPLE", persona.cumple or "")
    persona.zona = request.form.get("ZONA", persona.zona or "")
    persona.equipo = request.form.get("EQUIPO", persona.equipo or "")
    persona.talento = request.form.get("TALENTO", persona.talento or "")
    persona.observaciones = request.form.get("OBSERVACIONES", persona.observaciones or "")

    db.session.commit()
    return jsonify({"status": "ok", "mensaje": "Datos actualizados correctamente"})

# ==========================================
# RUTA DE AGREGAR INVITADO (ACTUALIZADA)
# ==========================================
@app.route('/agregar_invitado', methods=['POST'])
@login_required
@retry_on_429
def agregar_invitado():
    # 1. Recogemos TODOS los datos nuevos con la protección 'or ""'
    cedula = request.form.get('cedula') or ""
    nombre = (request.form.get('nombre') or "").upper()
    estado = request.form.get('estado') or ""
    genero = request.form.get('genero') or ""
    correo = request.form.get('correo') or ""
    celular = request.form.get('celular') or ""
    cumple = request.form.get('cumple') or ""
    zona = request.form.get('zona') or ""
    equipo = request.form.get('equipo') or ""
    talento = request.form.get('talento') or ""
    observaciones = request.form.get('observaciones') or ""
    
    # Origen (para saber a dónde volver)
    origen = request.form.get('evento_actual') 

    nuevo = Invitado(
        estado=estado,
        nombre=nombre,
        genero=genero,
        cedula=cedula,
        correo=correo,
        celular=celular,
        cumple=cumple,
        zona=zona,
        equipo=equipo,
        talento=talento,
        observaciones=observaciones,
    )
    db.session.add(nuevo)
    db.session.commit()

    if origen:
        return redirect(url_for('tomar_lista', nombre_evento=origen))
    else:
        flash(f"Invitado {nombre} agregado exitosamente")
        return redirect(url_for('index'))


@app.cli.command("init-db")
def init_db_command():
    """Inicializa las tablas en la base configurada por DATABASE_URL."""
    with app.app_context():
        db.create_all()
    print("DB inicializada (create_all).")
                
if __name__ == '__main__':
    port = int(os.environ.get('PORT', '5000'))
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(host='0.0.0.0', port=port, debug=debug, use_reloader=False)