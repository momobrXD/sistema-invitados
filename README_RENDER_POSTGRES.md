## Migración a PostgreSQL (Render)

### 1) Crear la base
- En Render: **New → PostgreSQL**
- Copia el **Internal Database URL**

### 2) Variables de entorno en el Web Service
- **`DATABASE_URL`**: pega el Internal Database URL
- (opcional) **`FLASK_DEBUG`**: `0`

> Nota: si Render te da `postgres://...`, el backend lo normaliza a `postgresql://...` automáticamente.

### 3) Build & Start
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: Render detecta `Procfile` (recomendado)  
  `web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 2`

### 4) Inicializar tablas
Render no ejecuta `flask init-db` solo. Tienes 2 opciones:

**Opción A (una vez, manual en Render Shell):**
- Abre **Shell** en tu Web Service y ejecuta:

```bash
python -m flask --app app init-db
```

**Opción B (temporal, como Start Command 1 vez):**
- Cambia Start Command a:

```bash
python -m flask --app app init-db && gunicorn app:app --bind 0.0.0.0:$PORT --workers 2
```

Luego de que arranque, vuelve al Start Command normal.

### 5) Datos
La base quedará vacía al inicio. Después puedes:
- Crear eventos desde la UI
- Agregar invitados desde la UI
- Importar datos desde Google Sheets con un script

#### Importar desde Google Sheets (Maestro/Eventos/Log)
Requiere credenciales (env `GOOGLE_CREDENTIALS` o archivo `credenciales-google.json`).

```bash
python scripts/import_from_sheets.py
```

Opcional: si tu Google Sheets no se llama `BaseMCC`, define:

```bash
GSHEET_NAME="TU_NOMBRE_DE_SHEET" python scripts/import_from_sheets.py
```

