import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import os

TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    raise ValueError("No se encontró DISCORD_TOKEN. Ejecuta: export DISCORD_TOKEN='tu_token'")

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

ALBION_API_URL = "https://gameinfo.albiononline.com/api/gameinfo/search?q="
WELCOME_CHANNEL_NAME = "registro-id"
CITIZEN_ROLE_NAME = "Ciudadano"

@bot.event
async def on_ready():
    print(f"✅ UNLIMITED conectado como {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🔄 Comandos sincronizados: {len(synced)}")
    except Exception as e:
        print(f"❌ Error al sincronizar: {e}")
    
    await setup_welcome_panel()

async def setup_welcome_panel():
    for guild in bot.guilds:
        channel = discord.utils.get(guild.text_channels, name=WELCOME_CHANNEL_NAME)
        if channel is None:
            print(f"⚠️ Canal #{WELCOME_CHANNEL_NAME} no encontrado en {guild.name}")
            continue
        
        async for message in channel.history(limit=10):
            if message.author == bot.user:
                await message.delete()
        
        embed = discord.Embed(
            title="🏙️ BIENVENIDO A UNLIMITED",
            description=(
                "**Donde la confianza se gana, no se impone.**\n\n"
                "Una comunidad meritocrática para jugadores de Albion Online.\n"
                "Aquí no hay líderes elegidos a dedo: tu reputación te abre camino.\n\n"
                "📜 *Regístrate para obtener el rol Ciudadano y desbloquear todos los canales.*"
            ),
            color=discord.Color.gold()
        )
        embed.set_image(url="https://cdn.discordapp.com/attachments/1530996763673104676/1530996825207607357/flor-coletta-armor-knight-adventurer-albion-gif.gif?ex=6a68ece7&is=6a679b67&hm=a0d074ad9bfe239fcd18d1a8bfdfb0a849fb2a3b3d58f6fe375ff82f06a4978b&")
        embed.set_footer(text="UNLIMITED • Albion Online")
        
        view = RegisterView()
        await channel.send(embed=embed, view=view)
        print(f"✅ Panel de bienvenida creado en #{channel.name}")

class RegisterModal(discord.ui.Modal, title="Registro de Ciudadano"):
    nick = discord.ui.TextInput(
        label="Tu nick exacto de Albion Online",
        placeholder="Ejemplo: Forjador",
        required=True,
        min_length=2,
        max_length=30
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        nick = self.nick.value.strip()
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{ALBION_API_URL}{nick}") as resp:
                    if resp.status != 200:
                        await interaction.followup.send("❌ Error al consultar la API de Albion. Intenta más tarde.", ephemeral=True)
                        return
                    data = await resp.json()
            except Exception:
                await interaction.followup.send("❌ No se pudo conectar con la API de Albion.", ephemeral=True)
                return
        
        if not data or "players" not in data or not data["players"]:
            await interaction.followup.send(f"❌ No se encontró al jugador **{nick}** en Albion Online. Verifica el nombre.", ephemeral=True)
            return
        
        player = data["players"][0]
        player_name = player.get("Name", nick)
        region = player.get("Region", "Desconocida")
        guild = player.get("GuildName", "Sin gremio")
        
        role = discord.utils.get(interaction.guild.roles, name=CITIZEN_ROLE_NAME)
        if role is None:
            await interaction.followup.send(f"❌ El rol **{CITIZEN_ROLE_NAME}** no existe. Contacta a un administrador.", ephemeral=True)
            return
        
        try:
            await interaction.user.add_roles(role)
        except Exception:
            await interaction.followup.send("❌ No tengo permisos para asignar roles.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="✅ ¡Registro exitoso!",
            description=(
                f"**{interaction.user.mention}, ahora eres Ciudadano de UNLIMITED.**\n\n"
                f"🎮 **Personaje:** {player_name}\n"
                f"🌍 **Región:** {region}\n"
                f"🏰 **Gremio:** {guild}\n\n"
                f"Todos los canales han sido desbloqueados para ti.\n"
                f"Participa, construye reputación y deja tu huella."
            ),
            color=discord.Color.green()
        )
        embed.set_footer(text="UNLIMITED • Albion Online")
        await interaction.followup.send(embed=embed, ephemeral=True)

class RegisterView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="📝 Registrarme como Ciudadano", style=discord.ButtonStyle.green, custom_id="register_button")
    async def register_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RegisterModal())

@bot.tree.command(name="panel", description="Vuelve a crear el panel de bienvenida en #bienvenida")
@app_commands.default_permissions(administrator=True)
async def panel(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    await setup_welcome_panel()
    await interaction.followup.send("✅ Panel de bienvenida recreado.", ephemeral=True)

if __name__ == "__main__":
    bot.run(TOKEN)
import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import sqlite3
import os

TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    raise ValueError("No se encontró DISCORD_TOKEN. Ejecuta: export DISCORD_TOKEN='tu_token'")

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

ALBION_API_URL = "https://gameinfo.albiononline.com/api/gameinfo/search?q="
REGISTER_CHANNEL_NAME = "registro-id"
VIP_CHANNEL_NAME = "💬-𝗽𝗼𝘀𝘁𝘂𝗹𝗮𝗰𝗶𝗼𝗻𝗲𝘀"
CITIZEN_ROLE_NAME = "Ciudadano"
VIP_ROLE_NAME = "Miembro VIP"

# Base de datos SQLite
conn = sqlite3.connect("unlimited.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS nominations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nominator_id TEXT,
    nominee_id TEXT,
    reason TEXT,
    message_id TEXT,
    votes TEXT DEFAULT '[]',
    status TEXT DEFAULT 'active'
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS revocations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    revoker_id TEXT,
    target_id TEXT,
    reason TEXT,
    message_id TEXT,
    votes TEXT DEFAULT '[]',
    status TEXT DEFAULT 'active'
)
""")
conn.commit()

def get_citizen_count(guild):
    role = discord.utils.get(guild.roles, name=CITIZEN_ROLE_NAME)
    if role:
        return len(role.members)
    return 0

def get_threshold(guild):
    count = get_citizen_count(guild)
    return max(3, int(count * 0.25))

@bot.event
async def on_ready():
    print(f"✅ UNLIMITED conectado como {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🔄 Comandos sincronizados: {len(synced)}")
    except Exception as e:
        print(f"❌ Error al sincronizar: {e}")
    
    await setup_welcome_panel()
    await setup_vip_panel()

async def setup_welcome_panel():
    for guild in bot.guilds:
        channel = discord.utils.get(guild.text_channels, name=REGISTER_CHANNEL_NAME)
        if channel is None:
            print(f"⚠️ Canal #{REGISTER_CHANNEL_NAME} no encontrado en {guild.name}")
            continue
        
        async for message in channel.history(limit=10):
            if message.author == bot.user:
                await message.delete()
        
        embed = discord.Embed(
            title="🏙️ BIENVENIDO A UNLIMITED",
            description=(
                "**Donde la confianza se gana, no se impone.**\n\n"
                "Una comunidad meritocrática para jugadores de Albion Online.\n"
                "Aquí no hay líderes elegidos a dedo: tu reputación te abre camino.\n\n"
                "📜 *Regístrate para obtener el rol Ciudadano y desbloquear todos los canales.*"
            ),
            color=discord.Color.gold()
        )
        embed.set_image(url="https://cdn.discordapp.com/attachments/1530996763673104676/1530996825207607357/flor-coletta-armor-knight-adventurer-albion-gif.gif?ex=6a68ece7&is=6a679b67&hm=a0d074ad9bfe239fcd18d1a8bfdfb0a849fb2a3b3d58f6fe375ff82f06a4978b&")
        embed.set_footer(text="UNLIMITED • Albion Online")
        
        view = RegisterView()
        await channel.send(embed=embed, view=view)
        print(f"✅ Panel de bienvenida creado en #{channel.name}")

async def setup_vip_panel():
    for guild in bot.guilds:
        channel = discord.utils.get(guild.text_channels, name=VIP_CHANNEL_NAME)
        if channel is None:
            print(f"⚠️ Canal {VIP_CHANNEL_NAME} no encontrado en {guild.name}")
            continue
        
        embed = discord.Embed(
            title="🏆 SALÓN DE LOS HONORABLES",
            description=(
                "*\"En Albion, el verdadero poder no se hereda ni se compra. "
                "Se forja en cada batalla, se demuestra en cada muerte y se gana "
                "con el respeto de quienes luchan a tu lado. "
                "Aquí no hay coronas regaladas: solo los que sangran juntos "
                "se convierten en leyenda.\"*\n\n"
                "📜 Usa `/nominar @usuario motivo` para proponer a un nuevo **Miembro VIP**.\n"
                "⚖️ Usa `/revocar @usuario motivo` para iniciar una moción de revocación."
            ),
            color=discord.Color.purple()
        )
        embed.set_image(url="https://cdn.discordapp.com/attachments/1530996763673104676/1531474555137429696/JCcKrBJ_copy_3000x1692.jpg?ex=6a695853&is=6a6806d3&hm=711800392ee3f8a99b89baf2af1610c64d14b80b9f85deca964b89785c0403bb&")
        embed.set_footer(text="UNLIMITED • Sistema Meritocrático")
        
        await channel.send(embed=embed)

class RegisterModal(discord.ui.Modal, title="Registro de Ciudadano"):
    nick = discord.ui.TextInput(
        label="Tu nick exacto de Albion Online",
        placeholder="Ejemplo: Forjador",
        required=True,
        min_length=2,
        max_length=30
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        nick = self.nick.value.strip()
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{ALBION_API_URL}{nick}") as resp:
                    if resp.status != 200:
                        await interaction.followup.send("❌ Error al consultar la API de Albion. Intenta más tarde.", ephemeral=True)
                        return
                    data = await resp.json()
            except Exception:
                await interaction.followup.send("❌ No se pudo conectar con la API de Albion.", ephemeral=True)
                return
        
        if not data or "players" not in data or not data["players"]:
            await interaction.followup.send(f"❌ No se encontró al jugador **{nick}** en Albion Online. Verifica el nombre.", ephemeral=True)
            return
        
        player = data["players"][0]
        player_name = player.get("Name", nick)
        region = player.get("Region", "Desconocida")
        guild = player.get("GuildName", "Sin gremio")
        
        role = discord.utils.get(interaction.guild.roles, name=CITIZEN_ROLE_NAME)
        if role is None:
            await interaction.followup.send(f"❌ El rol **{CITIZEN_ROLE_NAME}** no existe. Contacta a un administrador.", ephemeral=True)
            return
        
        try:
            await interaction.user.add_roles(role)
        except Exception:
            await interaction.followup.send("❌ No tengo permisos para asignar roles.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="✅ ¡Registro exitoso!",
            description=(
                f"**{interaction.user.mention}, ahora eres Ciudadano de UNLIMITED.**\n\n"
                f"🎮 **Personaje:** {player_name}\n"
                f"🌍 **Región:** {region}\n"
                f"🏰 **Gremio:** {guild}\n\n"
                f"Todos los canales han sido desbloqueados para ti.\n"
                f"Participa, construye reputación y deja tu huella."
            ),
            color=discord.Color.green()
        )
        embed.set_footer(text="UNLIMITED • Albion Online")
        await interaction.followup.send(embed=embed, ephemeral=True)

class RegisterView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="📝 Registrarme como Ciudadano", style=discord.ButtonStyle.green, custom_id="register_button")
    async def register_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RegisterModal())

class NominationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="👍 Apoyar", style=discord.ButtonStyle.green, custom_id="support_nomination")
    async def support_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        
        citizen_role = discord.utils.get(interaction.guild.roles, name=CITIZEN_ROLE_NAME)
        if citizen_role not in interaction.user.roles:
            await interaction.followup.send("❌ Solo los Ciudadanos pueden votar.", ephemeral=True)
            return
        
        message_id = str(interaction.message.id)
        cursor.execute("SELECT votes, nominee_id FROM nominations WHERE message_id = ? AND status = 'active'", (message_id,))
        row = cursor.fetchone()
        if not row:
            await interaction.followup.send("❌ Nominación no encontrada.", ephemeral=True)
            return
        
        votes = eval(row[0])
        nominee_id = row[1]
        
        if interaction.user.id in votes:
            await interaction.followup.send("⚠️ Ya has apoyado esta nominación.", ephemeral=True)
            return
        
        votes.append(interaction.user.id)
        cursor.execute("UPDATE nominations SET votes = ? WHERE message_id = ?", (str(votes), message_id))
        conn.commit()
        
        threshold = get_threshold(interaction.guild)
        
        embed = interaction.message.embeds[0]
        embed.set_field_at(0, name="📊 Progreso", value=f"{len(votes)}/{threshold} apoyos ({int(len(votes)/threshold*100)}%)", inline=False)
        await interaction.message.edit(embed=embed)
        
        if len(votes) >= threshold:
            vip_role = discord.utils.get(interaction.guild.roles, name=VIP_ROLE_NAME)
            nominee = interaction.guild.get_member(int(nominee_id))
            if vip_role and nominee:
                await nominee.add_roles(vip_role)
                embed.color = discord.Color.gold()
                embed.title = "✅ NUEVO MIEMBRO VIP"
                embed.set_field_at(0, name="📊 Progreso", value=f"✅ ¡Umbral alcanzado! {len(votes)}/{threshold} apoyos", inline=False)
                await interaction.message.edit(embed=embed)
                cursor.execute("UPDATE nominations SET status = 'approved' WHERE message_id = ?", (message_id,))
                conn.commit()
        
        await interaction.followup.send("✅ Tu apoyo ha sido registrado.", ephemeral=True)

class RevocationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="🗳️ Apoyar Revocación", style=discord.ButtonStyle.red, custom_id="support_revocation")
    async def support_revocation(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        
        citizen_role = discord.utils.get(interaction.guild.roles, name=CITIZEN_ROLE_NAME)
        if citizen_role not in interaction.user.roles:
            await interaction.followup.send("❌ Solo los Ciudadanos pueden votar.", ephemeral=True)
            return
        
        message_id = str(interaction.message.id)
        cursor.execute("SELECT votes, target_id FROM revocations WHERE message_id = ? AND status = 'active'", (message_id,))
        row = cursor.fetchone()
        if not row:
            await interaction.followup.send("❌ Moción no encontrada.", ephemeral=True)
            return
        
        votes = eval(row[0])
        target_id = row[1]
        
        if interaction.user.id in votes:
            await interaction.followup.send("⚠️ Ya has apoyado esta moción.", ephemeral=True)
            return
        
        votes.append(interaction.user.id)
        cursor.execute("UPDATE revocations SET votes = ? WHERE message_id = ?", (str(votes), message_id))
        conn.commit()
        
        threshold = get_threshold(interaction.guild)
        
        embed = interaction.message.embeds[0]
        embed.set_field_at(0, name="📊 Progreso", value=f"{len(votes)}/{threshold} apoyos ({int(len(votes)/threshold*100)}%)", inline=False)
        await interaction.message.edit(embed=embed)
        
        if len(votes) >= threshold:
            vip_role = discord.utils.get(interaction.guild.roles, name=VIP_ROLE_NAME)
            target = interaction.guild.get_member(int(target_id))
            if vip_role and target:
                await target.remove_roles(vip_role)
                embed.color = discord.Color.dark_red()
                embed.title = "❌ MIEMBRO VIP REVOCADO"
                embed.set_field_at(0, name="📊 Progreso", value=f"✅ Umbral alcanzado. Rol retirado.", inline=False)
                await interaction.message.edit(embed=embed)
                cursor.execute("UPDATE revocations SET status = 'approved' WHERE message_id = ?", (message_id,))
                conn.commit()
        
        await interaction.followup.send("✅ Tu apoyo ha sido registrado.", ephemeral=True)

@bot.tree.command(name="nominar", description="Nomina a un Ciudadano para ser Miembro VIP")
@app_commands.describe(usuario="El Ciudadano que deseas nominar", motivo="Por qué merece ser Miembro VIP")
async def nominar(interaction: discord.Interaction, usuario: discord.Member, motivo: str):
    await interaction.response.defer(ephemeral=True)
    
    citizen_role = discord.utils.get(interaction.guild.roles, name=CITIZEN_ROLE_NAME)
    if citizen_role not in interaction.user.roles:
        await interaction.followup.send("❌ Solo los Ciudadanos pueden nominar.", ephemeral=True)
        return
    
    if citizen_role not in usuario.roles:
        await interaction.followup.send("❌ Solo puedes nominar a un Ciudadano.", ephemeral=True)
        return
    
    vip_role = discord.utils.get(interaction.guild.roles, name=VIP_ROLE_NAME)
    if vip_role in usuario.roles:
        await interaction.followup.send("❌ Este usuario ya es Miembro VIP.", ephemeral=True)
        return
    
    channel = discord.utils.get(interaction.guild.text_channels, name=VIP_CHANNEL_NAME)
    if not channel:
        await interaction.followup.send(f"❌ Canal {VIP_CHANNEL_NAME} no encontrado.", ephemeral=True)
        return
    
    threshold = get_threshold(interaction.guild)
    
    embed = discord.Embed(
        title="🏆 Nominación a Miembro VIP",
        description=(
            f"**Candidato:** {usuario.mention}\n"
            f"**Nominado por:** {interaction.user.mention}\n"
            f"**Motivo:** {motivo}"
        ),
        color=discord.Color.blue()
    )
    embed.add_field(name="📊 Progreso", value=f"0/{threshold} apoyos (0%)", inline=False)
    embed.set_footer(text="UNLIMITED • Solo Ciudadanos pueden votar")
    
    view = NominationView()
    message = await channel.send(embed=embed, view=view)
    
    cursor.execute(
        "INSERT INTO nominations (nominator_id, nominee_id, reason, message_id) VALUES (?, ?, ?, ?)",
        (str(interaction.user.id), str(usuario.id), motivo, str(message.id))
    )
    conn.commit()
    
    await interaction.followup.send(f"✅ Nominación creada en {channel.mention}", ephemeral=True)

@bot.tree.command(name="revocar", description="Inicia una moción para revocar un Miembro VIP")
@app_commands.describe(usuario="El Miembro VIP que deseas revocar", motivo="Por qué debe perder el rol")
async def revocar(interaction: discord.Interaction, usuario: discord.Member, motivo: str):
    await interaction.response.defer(ephemeral=True)
    
    citizen_role = discord.utils.get(interaction.guild.roles, name=CITIZEN_ROLE_NAME)
    if citizen_role not in interaction.user.roles:
        await interaction.followup.send("❌ Solo los Ciudadanos pueden iniciar una moción.", ephemeral=True)
        return
    
    vip_role = discord.utils.get(interaction.guild.roles, name=VIP_ROLE_NAME)
    if vip_role not in usuario.roles:
        await interaction.followup.send("❌ Este usuario no es Miembro VIP.", ephemeral=True)
        return
    
    channel = discord.utils.get(interaction.guild.text_channels, name=VIP_CHANNEL_NAME)
    if not channel:
        await interaction.followup.send(f"❌ Canal {VIP_CHANNEL_NAME} no encontrado.", ephemeral=True)
        return
    
    threshold = get_threshold(interaction.guild)
    
    embed = discord.Embed(
        title="⚖️ Moción de Revocación",
        description=(
            f"**Miembro VIP:** {usuario.mention}\n"
            f"**Solicitado por:** {interaction.user.mention}\n"
            f"**Motivo:** {motivo}"
        ),
        color=discord.Color.red()
    )
    embed.add_field(name="📊 Progreso", value=f"0/{threshold} apoyos (0%)", inline=False)
    embed.set_footer(text="UNLIMITED • Solo Ciudadanos pueden votar")
    
    view = RevocationView()
    message = await channel.send(embed=embed, view=view)
    
    cursor.execute(
        "INSERT INTO revocations (revoker_id, target_id, reason, message_id) VALUES (?, ?, ?, ?)",
        (str(interaction.user.id), str(usuario.id), motivo, str(message.id))
    )
    conn.commit()
    
    await interaction.followup.send(f"✅ Moción de revocación creada en {channel.mention}", ephemeral=True)

@bot.tree.command(name="panel", description="Recrea los paneles de bienvenida y VIP")
@app_commands.default_permissions(administrator=True)
async def panel(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    await setup_welcome_panel()
    await setup_vip_panel()
    await interaction.followup.send("✅ Paneles recreados.", ephemeral=True)

if __name__ == "__main__":
    bot.run(TOKEN)
