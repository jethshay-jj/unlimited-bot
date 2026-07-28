import sqlite3
from config import DB_PATH

def get_connection():
    """Obtiene una conexión a la base de datos"""
    return sqlite3.connect(DB_PATH)

def execute_query(query, params=None):
    """Ejecuta una consulta y devuelve resultados"""
    conn = get_connection()
    c = conn.cursor()
    if params:
        c.execute(query, params)
    else:
        c.execute(query)
    result = c.fetchall()
    conn.commit()
    conn.close()
    return result

def get_user(user_id):
    """Obtiene un usuario por ID"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM usuarios WHERE user_id = ?", (str(user_id),))
    result = c.fetchone()
    conn.close()
    return result

def update_reputacion(user_id, delta):
    """Actualiza la reputación de un usuario"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE usuarios SET reputacion = reputacion + ? WHERE user_id = ?", 
              (delta, str(user_id)))
    conn.commit()
    conn.close()
