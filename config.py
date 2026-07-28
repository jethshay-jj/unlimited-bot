import os

TOKEN = os.getenv('DISCORD_TOKEN', 'TU_TOKEN_AQUI')
PREFIX = '!'
GUILD_ID = 1530996763673104676  # Reemplaza con tu server ID

# Canales
CHANNELS = {
    'registro': 'registro-id',
    'nominaciones': 'nominaciones',
    'mercado': 'mercado',
    'creadores': 'creadores',
    'leyenda': 'leyenda',
    'testigos': 'testigos'
}

# Roles
ROLES = {
    'ciudadano': 'Ciudadano',
    'vip': 'Miembro VIP',
    'creador': 'Creador',
    'leyenda': 'Leyenda del Mes'
}

# API Albion
ALBION_API = 'https://gameinfo.albiononline.com/api/gameinfo/search?q='
