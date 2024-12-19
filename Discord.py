import discord
from collections import deque

from discord.ext import commands
from discord.utils import get
import yt_dlp as youtube_dl

import Controls
import credenciales
from Spotify import obtener_informacion_spotify
from Youtube import reproducir, buscar_youtube

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="ms:", intents=intents)
playlist = deque()


intents = discord.Intents.default()
intents.message_content = True


# -------------------------- LLAMAR AL BOT AL SERVIDOR ------------------------- #
@bot.event
async def on_ready():
    print(f"✅ Bot listo y conectado como {bot.user}")
    for command in bot.commands:
        print(f"- {command.name}")
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game(name="¡Reproduciendo música!"),
    )


@bot.command()
async def conectar(ctx):
    global playlist

    canal = ctx.message.author.voice.channel

    if not canal:
        await ctx.send("❌ No estás conectado a un canal de voz.")
        return

    voz = get(bot.voice_clients, guild=ctx.guild)

    if voz and voz.is_connected():
        await voz.move_to(canal)
    else:
        voz = await canal.connect()

    playlist.clear()
    await ctx.send("🎶 Conectado al canal y lista de reproducción inicializada.")


@bot.command()
async def desconectar(ctx):
    """
    Desconecta al bot del canal de voz en el que está.
    """
    voz = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    if voz and voz.is_connected():
        await voz.disconnect()  # Desconecta al bot del canal de voz
        await ctx.send("🎶 El bot se ha desconectado del canal de voz.")
    else:
        await ctx.send("⚠️ El bot no está conectado a un canal de voz.")


# -------------------------- YOUTUBE -------------------------- #


@bot.command()
async def video(ctx):
    embed = discord.Embed(
        title="Video",
        description="https://www.youtube.com/watch?v=9-80NMLhmxs",
        color=discord.Color.blue(),
    )
    await ctx.send(embed=embed)


@bot.command()
async def youtube(ctx, url: str):

    try:
        # Verificamos que el usuario este conectado a un canal de voz
        if not ctx.author.voice or not ctx.author.voice.channel:
            embed = discord.Embed(
                title="Error",
                description="❌ Debes estar conectado a un canal de voz para usar este comando.",
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)
            return
        else:
            # Si esta conectado el usuario, llama a la función en youtube.py
            await reproducir(ctx, bot, url)
    # Errores al reproducir el video

    except youtube_dl.utils.DownloadError:
        # No se encontro canción en youtube
        embed = discord.Embed(
            title="Error",
            description="❌ No se pudo procesar la URL. Asegúrate de que sea válida y de YouTube.",
            color=discord.Color.red(),
        )
        await ctx.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="Error",
            description="❌ Ocurrió un error al intentar reproducir la canción desde YouTube.",
            color=discord.Color.red(),
        )
        await ctx.send(embed=embed)
        print(f"Error en youtube command: {e}")


# -------------------------- SPOTIFY -------------------------- #
@bot.command()
async def spotify(ctx, url: str):
    try:
        # Obtiene información de canciones desde el enlace de Spotify
        canciones = obtener_informacion_spotify(url)

        # Verifica si el usuario está conectado a un canal de voz
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send(
                "❌ Debes estar conectado a un canal de voz para usar este comando."
            )
            return

        if canciones:
            # Procesa cada canción obtenida
            for cancion in canciones:
                await ctx.send(f"🔍 Buscando **{cancion}** en YouTube...")
                titulo, enlace = await buscar_youtube(cancion)  # Corrección aquí
                if enlace:
                    await reproducir(ctx, bot, enlace, cancion)
                else:
                    await ctx.send(
                        f"⚠️ No se encontró un resultado válido para **{cancion}**."
                    )
        else:
            await ctx.send("⚠️ No se encontró información válida en Spotify.")

    except Exception as e:
        await ctx.send("❌ Error al procesar el enlace de Spotify.")
        print(f"Error en spotify command: {e}")


# -------------------------- CONTROLES DE LISTA DE REPRODUCCION --------------------------


@bot.command()
async def lista(ctx):
    try:
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send(
                "❌ Debes estar conectado a un canal de voz para usar este comando."
            )
            return
        else:
            await Controls.lista(ctx)
    except Exception as e:
        await ctx.send("❌ Error al mostrar la lista de reproducción.")
        print(f"Error en lista command: {e}")


@bot.command()
async def limpiar(ctx):
    try:
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send(
                "❌ Debes estar conectado a un canal de voz para usar este comando."
            )
            return
        else:
            await Controls.limpiar(ctx)
    except Exception as e:
        await ctx.send("❌ Error al limpiar la lista de reproducción.")
        print(f"Error en limpiar command: {e}")


@bot.command()
async def eliminar(ctx, posicion: int):
    try:
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send(
                "❌ Debes estar conectado a un canal de voz para usar este comando."
            )
            return
        else:
            await Controls.eliminar(ctx, posicion)
    except ValueError:
        await ctx.send("⚠️ La posición debe ser un número válido.")
    except Exception as e:
        await ctx.send("❌ Error al eliminar la canción.")
        print(f"Error en eliminar command: {e}")


@bot.command()
async def mover(ctx, posicion_actual: int, nueva_posicion: int):
    try:
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send(
                "❌ Debes estar conectado a un canal de voz para usar este comando."
            )
            return
        else:
            await Controls.mover(ctx, posicion_actual, nueva_posicion)
    except ValueError:
        await ctx.send("⚠️ Las posiciones deben ser números válidos.")
    except Exception as e:
        await ctx.send("❌ Error al mover la canción.")
        print(f"Error en mover command: {e}")


# -------------------------- CONTROLES DE REPRODUCCIÓN --------------------------
@bot.command()
async def pausar(ctx):
    try:
        voz = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send(
                "❌ Debes estar conectado a un canal de voz para usar este comando."
            )
            return
        else:
            await Controls.pausar(ctx, voz)
    except Exception as e:
        await ctx.send("❌ Error al pausar la reproducción.")
        print(f"Error en pausar command: {e}")


@bot.command()
async def reanudar(ctx):
    try:
        voz = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send(
                "❌ Debes estar conectado a un canal de voz para usar este comando."
            )
            return
        else:
            await Controls.reanudar(ctx, voz)
    except Exception as e:
        await ctx.send("❌ Error al reanudar la reproducción.")
        print(f"Error en reanudar command: {e}")


@bot.command()
async def saltar(ctx):
    try:
        voz = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send(
                "❌ Debes estar conectado a un canal de voz para usar este comando."
            )
            return
        else:
            await Controls.saltar(ctx, voz)
    except Exception as e:
        await ctx.send("❌ Error al saltar la canción.")
        print(f"Error en saltar command: {e}")


# -------------------------- MANEJO DE ERRORES GENERALES --------------------------
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(
            "⚠️ Comando no encontrado. Usa `ms:` para ver los comandos disponibles."
        )
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️ Faltan argumentos en el comando. Revisa la sintaxis.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("⚠️ Argumento inválido. Asegúrate de usar el formato correcto.")
    else:
        await ctx.send("❌ Ha ocurrido un error inesperado.")
        print(f"Error no manejado: {error}")


# -------------------------- LISTA DE COMANDOS -------------------------- #


@bot.command()
async def ayuda(ctx):
    """
    Muestra una lista de todos los comandos disponibles y sus descripciones.
    """
    embed = discord.Embed(
        title="🎵 Lista de Comandos del Bot 🎵",
        description="Aquí tienes todos los comandos disponibles:",
        color=discord.Color.blue(),
    )

    # Sección de comandos de YouTube
    embed.add_field(
        name="🎥 **Comandos de YouTube**",
        value=(
            "`ms:youtube <url>` - Reproduce una canción desde YouTube.\n"
            "`ms:saltar` - Salta la canción actual.\n"
            "`ms:detener` - Detiene la reproducción.\n"
            "`ms:pausar` - Pausa la canción actual.\n"
            "`ms:reanudar` - Reanuda la canción pausada."
        ),
        inline=False,
    )

    # Sección de comandos de Spotify
    embed.add_field(
        name="🎵 **Comandos de Spotify**",
        value=(
            "`ms:spotify <url>` - Reproduce una canción o playlist desde Spotify.\n"
            "⚠️ *Nota*: Convierte canciones de Spotify a enlaces de YouTube automáticamente."
        ),
        inline=False,
    )

    # Sección de controles del bot
    embed.add_field(
        name="🎮 **Controles del Bot**",
        value=(
            "`ms:conectar` - Conecta el bot al canal de voz.\n"
            "`ms:desconectar` - Desconecta el bot del canal de voz.\n"
            "`ms:lista` - Muestra la lista de reproducción actual.\n"
            "`ms:limpiar` - Elimina todas las canciones de la lista.\n"
            "`ms:video` - Muestra un video de ejemplo (¡broma!)."
        ),
        inline=False,
    )

    # Mensaje final
    embed.set_footer(
        text="Usa los comandos con el prefijo 'ms:' para interactuar conmigo 🎶"
    )
    await ctx.send(embed=embed)


# -------------------------- EJECUCIÓN DEL BOT --------------------------
try:
    bot.run(credenciales.DISCORD_BOT_TOKEN)
except Exception as e:
    print(f"❌ Error al iniciar el bot: {e}")
