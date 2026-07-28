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
WELCOME_CHANNEL_NAME = "bienvenida"
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
