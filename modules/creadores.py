import discord
from discord.ext import commands
import sqlite3
from datetime import datetime
from config import ROLES, DB_PATH

class Creadores(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='creador')
    async def creador(self, ctx, nombre_creador: str = None, especialidad: str = None):
        """Regístrate como creador de contenido"""
        if not nombre_creador or not especialidad:
            await ctx.send("❌ Usa: `!creador <nombre_creador> <especialidad>`")
            return
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Verificar registro
        c.execute("SELECT * FROM usuarios WHERE user_id = ?", (str(ctx.author.id),))
        if not c.fetchone():
            await ctx.send("❌ Debes registrarte primero con `!registrar`")
            conn.close()
            return
        
        # Verificar si ya es creador
        c.execute("SELECT * FROM creadores WHERE user_id = ?", (str(ctx.author.id),))
        if c.fetchone():
            await ctx.send("❌ Ya estás registrado como creador")
            conn.close()
            return
        
        # Registrar creador
        c.execute("INSERT INTO creadores (user_id, nombre_creador, especialidad, fecha_registro) VALUES (?, ?, ?, ?)",
                  (str(ctx.author.id), nombre_creador, especialidad, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        
        # Asignar rol
        guild = ctx.guild
        rol = discord.utils.get(guild.roles, name=ROLES['creador'])
        if rol:
            await ctx.author.add_roles(rol)
        
        await ctx.send(f"✅ Registrado como creador: **{nombre_creador}** - {especialidad}")

async def setup(bot):
    await bot.add_cog(Creadores(bot))
