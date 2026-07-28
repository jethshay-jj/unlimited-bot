import discord
from discord.ext import commands
import sqlite3
import aiohttp
from datetime import datetime
from config import DB_PATH

class Mercado(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='precio')
    async def precio(self, ctx, *, item: str = None):
        """Consulta el precio de un item en el mercado"""
        if not item:
            await ctx.send("❌ Usa: `!precio <nombre_del_item>`")
            return
        
        # Buscar en caché o API
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Verificar caché (menos de 1 hora)
        c.execute("SELECT precio_compra, precio_venta, ciudad, fecha_actualizacion FROM mercado_cache WHERE item_name = ? ORDER BY fecha_actualizacion DESC LIMIT 1",
                  (item.lower(),))
        cache = c.fetchone()
        conn.close()
        
        if cache:
            embed = discord.Embed(
                title=f"📊 Precio de {item.title()}",
                color=0x00ff00
            )
            embed.add_field(name="Precio Compra", value=f"{cache[0]:,}")
            embed.add_field(name="Precio Venta", value=f"{cache[1]:,}")
            embed.add_field(name="Ciudad", value=cache[2])
            embed.add_field(name="Última actualización", value=cache[3][:16])
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Item no encontrado. Probá con otro nombre.")

async def setup(bot):
    await bot.add_cog(Mercado(bot))
