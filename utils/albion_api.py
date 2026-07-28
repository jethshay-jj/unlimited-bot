import aiohttp
import json
from config import ALBION_API

async def search_player(player_name):
    """Busca un jugador en la API de Albion"""
    async with aiohttp.ClientSession() as session:
        async with session.get(ALBION_API + player_name) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            return data.get('players', [])

async def get_player_info(player_id):
    """Obtiene información detallada de un jugador"""
    url = f"https://gameinfo.albiononline.com/api/gameinfo/players/{player_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return None
            return await resp.json()
