import discord
from collections import deque

from discord.ext import commands
from discord.utils import get
import yt_dlp as youtube_dl

import Controls
import credenciales
from Spotify import obtener_informacion_spotify
from Youtube import reproducir, buscar_youtube, buscar_query


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="ms:", intents=intents)
playlist = deque()


intents = discord.Intents.default()
intents.message_content = True


# -------------------------- LLAMAR AL BOT AL SERVIDOR ------------------------- #


# Inicialización del bot
@bot.event
async def on_ready():
    print(f"✅ Bot listo y conectado como {bot.user}")  # Mensaje de confirmación
    for command in bot.commands:  # Lista de comandos disponibles por consola
        print(f"- {command.name}")
    await bot.change_presence(  # Estado del bot
        status=discord.Status.online,
        activity=discord.Game(name="`¡Reproduciendo música! 🎶`"),
    )


# Conección del bot al canal de voz
@bot.command()
async def conectar(ctx):
    global playlist  # Lista de reproducción global

    canal = ctx.message.author.voice.channel  # Canal de voz del usuario

    if not canal:  # Verificación de conexión al canal de voz
        embed = discord.Embed(
            title="Error",
            description="❌ No estás conectado a un canal de voz.",
            color=discord.Color.red(),
        )
        await ctx.send(embed=embed)
        return

    voz = get(bot.voice_clients, guild=ctx.guild)  # Conexión del bot al canal de voz

    if voz and voz.is_connected():  # Verificación de conexión del bot al canal de voz
        await voz.move_to(canal)
    else:
        voz = await canal.connect()

    playlist.clear()  # Limpieza de la lista de reproducción
    embed = discord.Embed(
        title="Conectado",
        description="🎶 Conectado al canal y lista de reproducción inicializada.",
        color=discord.Color.green(),
    )
    await ctx.send(embed=embed)  # Mensaje de estado de conexión


# Desconexión del bot al canal de voz
@bot.command()
async def desconectar(ctx):
    """
    Desconecta al bot del canal de voz en el que está.
    """
    voz = discord.utils.get(bot.voice_clients, guild=ctx.guild)

    if (
        voz and voz.is_connected()
    ):  # Verifica si el bot está conectado a un canal de voz
        embed = discord.Embed(
            title="Desconectando... 🎶",
            description="🎶 El bot se ha desconectado del canal de voz.",
            color=discord.Color.green(),
        )
        await voz.disconnect()  # Desconecta al bot del canal de voz
    else:
        embed = discord.Embed(
            title="Error",
            description="⚠️ El bot no está conectado a un canal de voz.",
            color=discord.Color.red(),
        )

    await ctx.send(embed=embed)


# -------------------------- YOUTUBE -------------------------- #


@bot.command()
async def video(ctx):  # Comando de broma para mostrar un video de ejemplo
    embed = discord.Embed(
        title="`Video 📽️`",
        description="https://www.youtube.com/watch?v=9-80NMLhmxs",
        color=discord.Color.blue(),
    )
    await ctx.send(embed=embed)


@bot.command()
async def youtube(
    ctx, url: str = None, *query
):  # Comando para reproducir canciones desde YouTube
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
            if query:  # Si se proporciona un termino de búsqueda
                titulo, url = await buscar_query(query)
                if url:  # Si se encuentra un resultado válido
                    await reproducir(ctx, bot, url, titulo)
                else:  # Si no se encuentra un resultado válido
                    await ctx.send(
                        "⚠️ No se encontró un resultado válido para la búsqueda."
                    )
            elif url:  # Si se proporciona una URL
                await reproducir(ctx, bot, url)
            else:  # Si no se proporciona una URL o una consulta de búsqueda
                embed = discord.Embed(
                    title="Error",
                    description="❌ Debes proporcionar una URL o una consulta de búsqueda.",
                    color=discord.Color.red(),
                )
                await ctx.send(embed=embed)

    # Errores al reproducir el video
    except youtube_dl.utils.DownloadError:
        # No se encontro canción en youtube
        embed = discord.Embed(
            title="Error",
            description="❌ No se pudo procesar la URL. Asegúrate de que sea válida y de YouTube.",
            color=discord.Color.red(),
        )
        await ctx.send(embed=embed)

    except Exception as e:  # Error general
        embed = discord.Embed(
            title="Error",
            description="❌ Ocurrió un error al intentar reproducir la canción desde YouTube.",
            color=discord.Color.red(),
        )
        await ctx.send(embed=embed)
        print(f"Error en youtube command: {e}")


# -------------------------- SPOTIFY -------------------------- #
@bot.command()
async def spotify(ctx, url: str):  # Comando para reproducir canciones desde Spotify
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

    except Exception as e:  # Error general
        await ctx.send("❌ Error al procesar el enlace de Spotify.")
        print(f"Error en spotify command: {e}")


# -------------------------- CONTROLES DE LISTA DE REPRODUCCION --------------------------


@bot.command()
async def lista(ctx):  # Comando para mostrar la lista de reproducción
    try:
        if (
            not ctx.author.voice or not ctx.author.voice.channel
        ):  # Verifica si el usuario está conectado a un canal de voz
            await ctx.send(
                "❌ Debes estar conectado a un canal de voz para usar este comando."
            )
            return
        else:
            await Controls.lista(
                ctx
            )  # Llama a la función en Controls.py para mostrar la lista de reproducción
    except Exception as e:  # Error general
        await ctx.send("❌ Error al mostrar la lista de reproducción.")
        print(f"Error en lista command: {e}")


@bot.command()
async def limpiar(ctx):  # Comando para limpiar la lista de reproducción
    try:
        if (
            not ctx.author.voice or not ctx.author.voice.channel
        ):  # Verifica si el usuario está conectado a un canal de voz
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
async def eliminar(ctx, posicion: int):  # Comando para eliminar una canción de la lista
    try:
        if (
            not ctx.author.voice or not ctx.author.voice.channel
        ):  # Verifica si el usuario está conectado a un canal de voz
            await ctx.send(
                "❌ Debes estar conectado a un canal de voz para usar este comando."
            )
            return
        else:
            await Controls.eliminar(
                ctx, posicion
            )  # Llama a la función en Controls.py para eliminar una canción de la lista
    except ValueError:
        await ctx.send(
            "⚠️ La posición debe ser un número válido."
        )  # Error si la posición no es un número válido
    except Exception as e:
        await ctx.send("❌ Error al eliminar la canción.")  # Error general
        print(f"Error en eliminar command: {e}")


@bot.command()
async def mover(
    ctx, posicion_actual: int, nueva_posicion: int
):  # Comando para mover una canción de la lista a otra posición
    try:
        if (
            not ctx.author.voice or not ctx.author.voice.channel
        ):  # Verifica si el usuario está conectado a un canal de voz
            await ctx.send(
                "❌ Debes estar conectado a un canal de voz para usar este comando."
            )
            return
        else:
            await Controls.mover(
                ctx, posicion_actual, nueva_posicion
            )  # Llama a la función en Controls.py para mover una canción de la lista
    except ValueError:
        await ctx.send("⚠️ Las posiciones deben ser números válidos.")
    except Exception as e:
        await ctx.send("❌ Error al mover la canción.")
        print(f"Error en mover command: {e}")


# -------------------------- CONTROLES DE REPRODUCCIÓN --------------------------
@bot.command()
async def pausar(ctx):  # Comando para pausar la reproducción
    try:
        voz = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if (
            not ctx.author.voice or not ctx.author.voice.channel
        ):  # Verifica si el usuario está conectado a un canal de voz
            await ctx.send(
                "❌ Debes estar conectado a un canal de voz para usar este comando."
            )
            return
        else:
            await Controls.pausar(
                ctx, voz
            )  # Llama a la función en Controls.py para pausar la reproducción
    except Exception as e:
        await ctx.send("❌ Error al pausar la reproducción.")
        print(f"Error en pausar command: {e}")


@bot.command()
async def reanudar(ctx):  # Comando para reanudar la reproducción
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
async def saltar(ctx):  # Comando para saltar la canción actual
    try:
        voz = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if (
            not ctx.author.voice or not ctx.author.voice.channel
        ):  # Verifica si el usuario está conectado a un canal de voz
            await ctx.send(
                "❌ Debes estar conectado a un canal de voz para usar este comando."
            )
            return
        else:
            await Controls.saltar(
                ctx, voz
            )  # Llama a la función en Controls.py para saltar la canción actual
    except Exception as e:
        await ctx.send("❌ Error al saltar la canción.")
        print(f"Error en saltar command: {e}")


# -------------------------- MANEJO DE ERRORES GENERALES --------------------------


@bot.event
async def on_command_error(ctx, error):
    if isinstance(
        error, commands.CommandNotFound
    ):  # Comando no encontrado, muestra mensaje de para obtener ayuda
        await ctx.send(
            "⚠️ Comando no encontrado. Usa `ms:ayuda` para ver los comandos disponibles."
        )
    elif isinstance(
        error, commands.MissingRequiredArgument
    ):  # Faltan argumentos en el comando
        await ctx.send("⚠️ Faltan argumentos en el comando. Revisa la sintaxis.")
    elif isinstance(error, commands.BadArgument):  # Argumento inválido
        await ctx.send("⚠️ Argumento inválido. Asegúrate de usar el formato correcto.")
    else:
        await ctx.send("❌ Ha ocurrido un error inesperado.")  # Error inesperado
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
            "`ms:youtube <búsqueda>` - Busca y reproduce una canción desde YouTube.\n"
        ),
        inline=False,
    )

    # Sección de comandos de Spotify
    embed.add_field(
        name="🎵 **Comandos de Spotify**",
        value=(
            "`ms:spotify <url>` - Reproduce una canción o playlist desde Spotify.\n"
            "⚠️ *Nota*: Convierte canciones de Spotify a enlaces de YouTube automáticamente.\n"
        ),
        inline=False,
    )

    # Sección de controles de la lista de reproducción
    embed.add_field(
        name="🎶 **Controles de la Lista de Reproducción**",
        value=(
            "`ms:lista` - Muestra la lista de reproducción actual.\n"
            "`ms:limpiar` - Elimina todas las canciones de la lista.\n"
            "`ms:saltar` - Salta la canción actual.\n"
            "`ms:pausar` - Pausa la canción actual.\n"
            "`ms:reanudar` - Reanuda la canción pausada.\n"
            "`ms:mover <posición_actual> <nueva_posición>` - Mueve una canción a otra posición en la lista (⚠️se recomienda usar ms:lista antes).\n"
            "`ms:eliminar <posición>` - Elimina una canción de la lista.\n"
        ),
    )

    # Sección de controles del bot
    embed.add_field(
        name="🎮 **Controles del Bot**",
        value=(
            "`ms:conectar` - Conecta el bot al canal de voz.\n"
            "`ms:desconectar` - Desconecta el bot del canal de voz.\n"
            "`ms:video` - Muestra un video de ejemplo (¡broma!)."
        ),
        inline=False,
    )

    # Sección de comando del bot
    embed.set_footer(text="Usa los comandos con el prefijo 'ms:' para comenzar 🎶")

    await ctx.send(embed=embed)


# -------------------------- EJECUCIÓN DEL BOT --------------------------
# Iniciar el bot con las credenciales cargadas
try:
    bot.run(credenciales.DISCORD_BOT_TOKEN)
except Exception as e:
    print(f"❌ Error al iniciar el bot: {e}")
