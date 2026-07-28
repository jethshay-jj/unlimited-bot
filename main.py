import discord
from discord.ext import commands
import sqlite3
import os
from config import TOKEN, PREFIX, GUILD_ID, DB_PATH

# Configurar intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Lista de módulos
MODULES = ['registro', 'nominaciones', 'mercado', 'creadores', 'leyenda', 'testigos']

@bot.event
async def on_ready():
    print(f'✅ Bot UNLIMITED conectado como {bot.user}')
    print(f'✅ Servidor: {bot.guilds[0].name if bot.guilds else "Ninguno"}')
    await bot.change_presence(activity=discord.Game(name="!help | Albion Online"))
    
    # Inicializar base de datos
    init_db()
    
    # Cargar módulos
    for module in MODULES:
        try:
            await bot.load_extension(f'modules.{module}')
            print(f'✅ Módulo {module} cargado')
        except Exception as e:
            print(f'❌ Error cargando {module}: {e}')

def init_db():
    """Inicializa la base de datos SQLite"""
    os.makedirs('data', exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Usuarios
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
        user_id TEXT PRIMARY KEY,
        username TEXT,
        discord_name TEXT,
        registro_fecha TEXT,
        es_vip INTEGER DEFAULT 0,
        es_creador INTEGER DEFAULT 0,
        es_leyenda INTEGER DEFAULT 0,
        reputacion INTEGER DEFAULT 0
    )''')
    
    # Votos VIP
    c.execute('''CREATE TABLE IF NOT EXISTS votos_vip (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidato_id TEXT,
        votante_id TEXT,
        fecha TEXT,
        UNIQUE(candidato_id, votante_id)
    )''')
    
    # Reportes
    c.execute('''CREATE TABLE IF NOT EXISTS reportes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        acusado_id TEXT,
        denunciante_id TEXT,
        motivo TEXT,
        fecha TEXT,
        confirmaciones INTEGER DEFAULT 0,
        estado TEXT DEFAULT 'pendiente'
    )''')
    
    # Creadores
    c.execute('''CREATE TABLE IF NOT EXISTS creadores (
        user_id TEXT PRIMARY KEY,
        nombre_creador TEXT,
        especialidad TEXT,
        fecha_registro TEXT,
        misiones_completadas INTEGER DEFAULT 0
    )''')
    
    # Mercado (cache)
    c.execute('''CREATE TABLE IF NOT EXISTS mercado_cache (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT,
        precio_compra INTEGER,
        precio_venta INTEGER,
        ciudad TEXT,
        fecha_actualizacion TEXT,
        UNIQUE(item_name, ciudad)
    )''')
    
    conn.commit()
    conn.close()
    print('✅ Base de datos inicializada')

@bot.command(name='ping')
async def ping(ctx):
    """Verifica la latencia del bot"""
    await ctx.send(f'🏓 Pong! Latencia: {round(bot.latency * 1000)}ms')

@bot.command(name='info')
async def info(ctx):
    """Muestra información del bot"""
    embed = discord.Embed(
        title='📊 UNLIMITED Bot',
        description='Bot para Albion Online - Comunidad Meritocrática',
        color=0x00ff00
    )
    embed.add_field(name='Versión', value='v1.0')
    embed.add_field(name='Módulos', value='6 activos')
    embed.add_field(name='Filosofía', value='"Donde la confianza se gana, no se impone"')
    embed.set_footer(text='Desarrollado con ❤️ para la comunidad')
    await ctx.send(embed=embed)

if __name__ == '__main__':
    try:
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("❌ Token inválido. Verificá tu .env")
    except Exception as e:
        print(f"❌ Error: {e}")
