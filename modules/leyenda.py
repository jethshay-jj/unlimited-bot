import discord
from discord.ext import commands
import sqlite3
from datetime import datetime
from config import ROLES, DB_PATH

class Leyenda(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='leyenda')
    async def leyenda(self, ctx):
        """Muestra la Leyenda del Mes actual"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Obtener el usuario con más reputación del mes
        c.execute("SELECT discord_name, reputacion FROM usuarios ORDER BY reputacion DESC LIMIT 1")
        leyenda = c.fetchone()
        conn.close()
        
        if not leyenda:
            await ctx.send("📭 No hay leyenda aún")
            return
        
        embed = discord.Embed(
            title="🏅 LEYENDA DEL MES",
            description=f"**{leyenda[0]}**",
            color=0xffd700
        )
        embed.add_field(name="Reputación", value=f"⭐ {leyenda[1]}")
        embed.add_field(name="Mes", value=datetime.now().strftime("%B %Y"))
        embed.set_footer(text="Actualizado automáticamente el día 1 de cada mes")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Leyenda(bot))
