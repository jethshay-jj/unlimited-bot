import discord
from discord.ext import commands
import sqlite3
from datetime import datetime, timedelta
from config import DB_PATH

class Testigos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reportes_pendientes = {}
    
    @commands.command(name='reportar')
    async def reportar(self, ctx, acusado: discord.Member = None, *, motivo: str = None):
        """Reporta a un jugador (requiere 2 confirmaciones)"""
        if not acusado or not motivo:
            await ctx.send("❌ Usa: `!reportar @usuario <motivo>`")
            return
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Verificar protección novato (<7 días)
        c.execute("SELECT registro_fecha FROM usuarios WHERE user_id = ?", (str(acusado.id),))
        data = c.fetchone()
        if data:
            fecha_reg = datetime.fromisoformat(data[0])
            if (datetime.now() - fecha_reg).days < 7:
                await ctx.send("🛡️ Este usuario está bajo el **Escudo del Novato** (menos de 7 días)")
                conn.close()
                return
        
        # Verificar que el denunciante esté registrado
        c.execute("SELECT * FROM usuarios WHERE user_id = ?", (str(ctx.author.id),))
        if not c.fetchone():
            await ctx.send("❌ Debes registrarte primero con `!registrar`")
            conn.close()
            return
        
        # Guardar reporte
        c.execute("INSERT INTO reportes (acusado_id, denunciante_id, motivo, fecha) VALUES (?, ?, ?, ?)",
                  (str(acusado.id), str(ctx.author.id), motivo, datetime.now().isoformat()))
        reporte_id = c.lastrowid
        conn.commit()
        conn.close()
        
        embed = discord.Embed(
            title="⚠️ NUEVO REPORTE",
            description=f"**Acusado:** {acusado.mention}\n**Motivo:** {motivo}\n**Reportado por:** {ctx.author.mention}",
            color=0xff0000
        )
        embed.add_field(name="Confirmaciones", value="0/2 necesarias")
        embed.add_field(name="Acción", value="Reacciona con ✅ para confirmar")
        embed.set_footer(text=f"ID: {reporte_id}")
        
        msg = await ctx.send(embed=embed)
        await msg.add_reaction('✅')
        
        self.reportes_pendientes[reporte_id] = {
            'msg_id': msg.id,
            'confirmaciones': set([ctx.author.id])
        }
    
    @commands.command(name='misreportes')
    async def misreportes(self, ctx):
        """Muestra tus reportes activos"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, acusado_id, motivo, fecha, estado FROM reportes WHERE denunciante_id = ? AND estado = 'pendiente'",
                  (str(ctx.author.id),))
        reportes = c.fetchall()
        conn.close()
        
        if not reportes:
            await ctx.send("📭 No tienes reportes pendientes")
            return
        
        msg = "📋 **TUS REPORTES PENDIENTES**\n"
        for r in reportes:
            msg += f"`#{r[0]}` - <@{r[1]}> - {r[2][:30]}... ({r[3][:10]})\n"
        await ctx.send(msg)

async def setup(bot):
    await bot.add_cog(Testigos(bot))
