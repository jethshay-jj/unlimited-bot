import discord
from discord.ext import commands
import sqlite3
import aiohttp
from datetime import datetime
from config import ALBION_API, ROLES, DB_PATH

class Registro(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='registrar')
    async def registrar(self, ctx, nombre_albion: str = None):
        """Registra un usuario en el sistema"""
        if not nombre_albion:
            await ctx.send("❌ Usa: `!registrar <nombre_albion>`")
            return
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Verificar si ya está registrado
        c.execute("SELECT * FROM usuarios WHERE user_id = ?", (str(ctx.author.id),))
        if c.fetchone():
            await ctx.send("❌ Ya estás registrado")
            conn.close()
            return
        
        # Buscar en API de Albion
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(ALBION_API + nombre_albion) as resp:
                    if resp.status != 200:
                        await ctx.send("❌ Error consultando API de Albion")
                        conn.close()
                        return
                    data = await resp.json()
        except:
            await ctx.send("❌ Error de conexión con la API")
            conn.close()
            return
        
        if not data.get('players'):
            await ctx.send(f"❌ Jugador '{nombre_albion}' no encontrado")
            conn.close()
            return
        
        # Registrar usuario
        fecha = datetime.now().isoformat()
        c.execute("INSERT INTO usuarios (user_id, username, discord_name, registro_fecha) VALUES (?, ?, ?, ?)",
                  (str(ctx.author.id), nombre_albion, ctx.author.name, fecha))
        conn.commit()
        conn.close()
        
        # Asignar rol Ciudadano
        guild = ctx.guild
        rol = discord.utils.get(guild.roles, name=ROLES['ciudadano'])
        if rol:
            await ctx.author.add_roles(rol)
        
        await ctx.send(f"✅ Registrado como **{nombre_albion}**! Bienvenido, {ctx.author.mention}")
    
    @commands.command(name='miperfil')
    async def miperfil(self, ctx):
        """Muestra tu perfil"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM usuarios WHERE user_id = ?", (str(ctx.author.id),))
        user = c.fetchone()
        conn.close()
        
        if not user:
            await ctx.send("❌ No estás registrado. Usa `!registrar <nombre>`")
            return
        
        embed = discord.Embed(title=f"📊 Perfil de {ctx.author.name}", color=0x00ff00)
        embed.add_field(name="Nombre Albion", value=user[1])
        embed.add_field(name="Fecha Registro", value=user[3][:10])
        embed.add_field(name="Reputación", value=user[6])
        embed.add_field(name="VIP", value="✅" if user[4] else "❌")
        embed.add_field(name="Creador", value="✅" if user[5] else "❌")
        embed.add_field(name="Leyenda", value="✅" if user[6] else "❌")
        await ctx.send(embed=embed)
    
    @commands.command(name='top')
    async def top(self, ctx):
        """Top 10 de reputación"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT discord_name, reputacion FROM usuarios ORDER BY reputacion DESC LIMIT 10")
        top = c.fetchall()
        conn.close()
        
        if not top:
            await ctx.send("📭 No hay usuarios registrados")
            return
        
        msg = "🏆 **TOP 10 REPUTACIÓN**\n"
        emojis = ['🥇', '🥈', '🥉']
        for i, (nombre, rep) in enumerate(top, 1):
            emoji = emojis[i-1] if i <= 3 else f'#{i}'
            msg += f"{emoji} {nombre} - ⭐ {rep}\n"
        await ctx.send(msg)

async def setup(bot):
    await bot.add_cog(Registro(bot))
