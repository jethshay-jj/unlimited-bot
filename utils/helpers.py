import re
from datetime import datetime

def validar_nombre_albion(nombre):
    """Valida que el nombre de Albion sea válido"""
    # Los nombres pueden tener letras, números, guiones y guiones bajos
    patron = r'^[a-zA-Z0-9_-]{3,16}$'
    return re.match(patron, nombre) is not None

def formatear_fecha(fecha_iso):
    """Formatea una fecha ISO a formato legible"""
    try:
        dt = datetime.fromisoformat(fecha_iso)
        return dt.strftime("%d/%m/%Y %H:%M")
    except:
        return fecha_iso

def calcular_edad_registro(fecha_iso):
    """Calcula días desde el registro"""
    try:
        dt = datetime.fromisoformat(fecha_iso)
        dias = (datetime.now() - dt).days
        return dias
    except:
        return 0
