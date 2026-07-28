import discord
from discord.ext import commands
import sqlite3
from datetime import datetime, timedelta
from config import ROLES, DB_PATH

class Nominaciones(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.votos_activos = {}
    
    @commands.command(name='nominar')
    async def nominar(self, ctx, miembro: discord.Member = None):
        """Nomina a alguien para VIP (requiere 25% de votos)"""
        if not miembro:
            await ctx.send("❌ Usa: `!nominar @usuario`")
            return
        
        if miembro == ctx.author:
            await ctx.send("❌ No puedes nominarte a ti mismo")
            return
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Verificar que el nominador esté registrado
        c.execute("SELECT * FROM usuarios WHERE user_id = ?", (str(ctx.author.id),))
        if not c.fetchone():
            await ctx.send("❌ Debes registrarte primero con `!registrar`")
            conn.close()
            return
        
        # Verificar que el nominado esté registrado
        c.execute("SELECT * FROM usuarios WHERE user_id = ?", (str(miembro.id),))
        if not c.fetchone():
            await ctx.send(f"❌ {miembro.mention} no está registrado")
            conn.close()
            return
        
        # Verificar que no sea ya VIP
        c.execute("SELECT es_vip FROM usuarios WHERE user_id = ?", (str(miembro.id),))
        if c.fetchone()[0] == 1:
            await ctx.send(f"❌ {miembro.mention} ya es VIP")
            conn.close()
            return
        
        conn.close()
        
        # Crear votación
        votacion_id = f"{ctx.channel.id}_{datetime.now().timestamp()}"
        self.votos_activos[votacion_id] = {
            'candidato': miembro.id,
            'votos': set([ctx.author.id]),
            'inicio': datetime.now()
        }
        
        embed = discord.Embed(
            title="🗳️ NUEVA NOMINACIÓN VIP",
            description=f"{ctx.author.mention} ha nominado a {miembro.mention}",
            color=0xffd700
        )
        embed.add_field(name="Requisitos", value="• 25% de votos afirmativos\n• Votación dura 24h\n• Votan usuarios registrados")
        embed.add_field(name="Votar", value="Reacciona con ✅ para votar a favor")
        embed.set_footer(text="Usa !revocar [usuario] para revocar")
        
        msg = await ctx.send(embed=embed)
        await msg.add_reaction('✅')
    
    @commands.command(name='revocar')
    async def revocar(self, ctx, miembro: discord.Member = None):
        """Revoca el rol VIP de alguien"""
        if not miembro:
            await ctx.send("❌ Usa: `!revocar @usuario`")
            return
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("UPDATE usuarios SET es_vip = 0 WHERE user_id = ?", (str(miembro.id),))
        conn.commit()
        conn.close()
        
        # Quitar rol
        guild = ctx.guild
        rol = discord.utils.get(guild.roles, name=ROLES['vip'])
        if rol and miembro in guild.members:
            await miembro.remove_roles(rol)
        
        await ctx.send(f"✅ Rol VIP revocado a {miembro.mention}")

async def setup(bot):
    await bot.add_cog(Nominaciones(bot))
