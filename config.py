import os

TOKEN = os.getenv('MTUzMDk4Mjc4MjE0OTQ2NDA2NA.GIZhFn.s8z5X2zWmKx6jN6qLwo-ISvORdxI7EPDY84IGA')
PREFIX = '!'
GUILD_ID = 1482867699293098044# Reemplaza con tu server ID

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
