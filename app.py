from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import gspread
from google.oauth2.service_account import Credentials
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import time
import os
import json
from functools import wraps

app = Flask(__name__)
app.secret_key = 'mcc_sistema_2026_pro_secure'

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

gsm = GSheetManager()

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
        # Intenta cargar configuración, si falla usa lista vacía
        ws_config = gsm.get_ws("Config")
        tipos = ws_config.col_values(1) if ws_config else []
        
        todos_eventos = gsm.get_batch_data("Eventos_Creados")
        abiertos = [e for e in todos_eventos if e.get('Estado') != 'Cerrado']
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

    ws = gsm.get_ws("Eventos_Creados")
    ws.append_row([nombre, tipo, fecha_final, "Abierto"])
    flash(f"Evento {nombre} creado correctamente")
    return redirect(url_for('index'))

# ==========================================
# RUTAS DE ASISTENCIA Y CONSULTA
# ==========================================

@app.route('/tomar_lista/<nombre_evento>')
@login_required
def tomar_lista(nombre_evento):
    eventos = gsm.get_batch_data("Eventos_Creados")
    evento_info = next((e for e in eventos if e['Nombre_Evento'] == nombre_evento), None)
    
    invitados = gsm.get_batch_data("Maestro")
    log_data = gsm.get_batch_data("Eventos_Log")
    
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

    asistentes_ids = [str(f['ID_Invitado']) for f in log_data if f['Evento_Especifico'] == nombre_evento]
    
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
    
    ws_log = gsm.get_ws("Eventos_Log")
    
    if accion == 'registrar':
        maestro = gsm.get_batch_data("Maestro")
        fecha_hoy = datetime.now().strftime('%d/%m/%Y')
        mes_hoy = datetime.now().strftime('%B')
        
        nuevas_filas = []
        for inv in maestro:
            if str(inv['Nro']) in ids_sel:
                # Estructura del LOG
                nuevas_filas.append([
                    fecha_hoy, ev_nombre, ev_tipo, 
                    inv['Nro'], inv['CEDULA'], 
                    inv['NOMBRE Y APELLIDO'], mes_hoy
                ])
        
        if nuevas_filas:
            ws_log.append_rows(nuevas_filas)
    
    elif accion == 'quitar': # <--- ESTO FALTABA EN TU CÓDIGO ORIGINAL
        all_logs = ws_log.get_all_values()
        headers = all_logs[0]
        rows_to_keep = [headers]
        
        # Índices asumiendo orden: Fecha, Evento, Tipo, ID...
        # Ajustar si tu Log es diferente. Aquí asumo col B=Evento(1) y D=ID(3)
        for row in all_logs[1:]:
            # Si NO coincide con lo que queremos borrar, lo guardamos
            if not (len(row) > 3 and row[1] == ev_nombre and str(row[3]) in ids_sel):
                rows_to_keep.append(row)
        
        ws_log.clear()
        ws_log.update('A1', rows_to_keep)
            
    return jsonify({"status": "ok"})

# --- RUTAS DE HISTORIAL QUE YA TENÍAS ---

@app.route('/historial_usuario/<id_inv>')
@login_required
def historial_usuario(id_inv):
    log_data = gsm.get_batch_data("Eventos_Log")
    participaciones = [
        {"Fecha": f['Fecha'], "Evento": f['Evento_Especifico']} 
        for f in log_data if str(f['ID_Invitado']) == str(id_inv)
    ]
    return jsonify(participaciones)

@app.route('/cumpleañeros')
@login_required
def cumpleañeros():
    """Muestra todas las personas que tienen cumpleaños en el mes actual"""
    personas = gsm.get_batch_data("Maestro")
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
def consultas():
    eventos = gsm.get_batch_data("Eventos_Creados")
    cerrados = [e for e in eventos if e.get('Estado') == 'Cerrado']
    personas = gsm.get_batch_data("Maestro")
    return render_template('consultas.html', eventos=cerrados, personas=personas)

@app.route('/detalle_evento_cerrado/<nombre_evento>')
@login_required
@retry_on_429
def detalle_evento_cerrado(nombre_evento):
    log_data = gsm.get_batch_data("Eventos_Log")
    # 1. Filtramos los que asistieron a este evento
    asistentes = [f for f in log_data if f['Evento_Especifico'] == nombre_evento]
    
    # 2. Lógica para detectar cumpleañeros entre los asistentes
    mes_actual = datetime.now().month
    meses_es = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    
    # Obtenemos datos del Maestro para cruzar las fechas de cumpleaños
    maestro = gsm.get_batch_data("Maestro")
    # Creamos un diccionario rápido de cumpleaños por ID
    cumples_dict = {str(p['Nro']): p.get('CUMPLE', '') for p in maestro}
    
    cumpleañeros_asistentes = []
    for asis in asistentes:
        id_inv = str(asis.get('ID_Invitado'))
        fecha_cumple_raw = cumples_dict.get(id_inv, '')
        
        mes, dia = procesar_fecha(fecha_cumple_raw)
        if mes == mes_actual:
            # Marcamos al asistente como cumpleañero
            asis['es_cumple'] = True
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
def historial_personal(id_inv):
    maestro = gsm.get_batch_data("Maestro")
    persona = next((p for p in maestro if str(p['Nro']) == str(id_inv)), None)
    log_data = gsm.get_batch_data("Eventos_Log")
    participaciones = [f for f in log_data if str(f['ID_Invitado']) == str(id_inv)]
    return render_template('detalle_historial.html', persona=persona, lista=participaciones, tipo="persona")

@app.route('/cerrar_evento', methods=['POST'])
@login_required
@retry_on_429
def cerrar_evento():
    nombre = request.form.get('nombre_evento')
    ws = gsm.get_ws("Eventos_Creados")
    try:
        cell = ws.find(nombre)
        ws.update_cell(cell.row, 4, "Cerrado")
    except:
        pass
    return redirect(url_for('index'))

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

    ws_maestro = gsm.get_ws("Maestro")
    all_data = ws_maestro.get_all_values()
    
    # 2. Generar ID automático
    try:
        ultimo_id = int(all_data[-1][0]) if len(all_data) > 1 and all_data[-1][0].isdigit() else 0
    except:
        ultimo_id = 0
    nuevo_id = ultimo_id + 1

    # 3. GUARDAR CON EL ORDEN DE LA IMAGEN
    # Orden: Nro | ESTADO | NOMBRE | GENERO | CEDULA | CORREO | CELULAR | CUMPLE | ZONA | EQUIPO | TALENTO | OBSERVACIONES
    fila_nueva = [
        nuevo_id, 
        estado, 
        nombre, 
        genero, 
        cedula, 
        correo, 
        celular, 
        cumple, 
        zona, 
        equipo, 
        talento, 
        observaciones
    ]

    ws_maestro.append_row(fila_nueva)

    if origen:
        return redirect(url_for('tomar_lista', nombre_evento=origen))
    else:
        flash(f"Invitado {nombre} agregado exitosamente")
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)