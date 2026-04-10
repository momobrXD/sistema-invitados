from datetime import datetime


def procesar_fecha(fecha_str: str | None) -> tuple[int | None, int]:
    """Convierte cualquier formato de fecha en (mes, día). Retorna (None, 99) si no se puede parsear."""
    if not fecha_str:
        return None, 99
    fecha_str = str(fecha_str).strip().lower()

    meses_texto = {
        'ene': 1, 'enero': 1, 'feb': 2, 'febrero': 2, 'mar': 3, 'marzo': 3,
        'abr': 4, 'abril': 4, 'may': 5, 'mayo': 5, 'jun': 6, 'junio': 6,
        'jul': 7, 'julio': 7, 'ago': 8, 'agosto': 8, 'sep': 9, 'septiembre': 9,
        'oct': 10, 'octubre': 10, 'nov': 11, 'noviembre': 11, 'dic': 12, 'diciembre': 12,
    }

    formatos = [
        '%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%Y/%m/%d',
        '%d/%m', '%d-%m', '%m/%d/%Y', '%m-%d-%Y',
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
            if mes:
                return mes, dia
    except Exception:
        pass

    return None, 99


MESES_ES = [
    '', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
]
