import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Token desde variable de entorno (SEGURO)
TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    raise ValueError("❌ DISCORD_TOKEN no encontrado. Creá un archivo .env")

GUILD_ID = int(os.getenv('GUILD_ID', 0))
if GUILD_ID == 0:
    raise ValueError("❌ GUILD_ID no encontrado. Creá un archivo .env")

PREFIX = '!'

# Canales (MODIFICAR con los nombres de tus canales)
CHANNELS = {
    'registro': 'registro-id',
    'nominaciones': 'nominaciones',
    'mercado': 'mercado',
    'creadores': 'creadores',
    'leyenda': 'leyenda',
    'testigos': 'testigos'
}

# Roles (MODIFICAR con los nombres de tus roles)
ROLES = {
    'ciudadano': 'Ciudadano',
    'vip': 'Miembro VIP',
    'creador': 'Creador',
    'leyenda': 'Leyenda del Mes'
}

# API Albion (NO MODIFICAR)
ALBION_API = 'https://gameinfo.albiononline.com/api/gameinfo/search?q='

# Configuración de base de datos
DB_PATH = 'data/unlimited.db'
