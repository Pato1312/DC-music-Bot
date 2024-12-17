from discord.utils import get
from collections import deque
import yt_dlp as youtube_dl
import discord

playlist = deque()  # Cola global para la lista de reproducción


async def reproducir(ctx, bot, url):
    canal = ctx.message.author.voice.channel
    if not canal:
        await ctx.send("No estás conectado a un canal de voz.")
        return

    voz = get(bot.voice_clients, guild=ctx.guild)
    if not voz or not voz.is_connected():
        voz = await canal.connect()

    ydl_opts = {"format": "bestaudio/best", "noplaylist": "True", "quiet": True}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        titulo = info["title"]

    playlist.append((titulo, url))
    await ctx.send(f"🎶 Se añadió **{titulo}** a la lista.")

    if not voz.is_playing():
        await reproducir_siguiente(ctx, voz)


async def reproducir_siguiente(ctx, voz):
    if playlist:
        titulo, url = playlist.popleft()

        ydl_opts = {"format": "bestaudio/best", "noplaylist": "True", "quiet": True}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            stream_url = info["url"]

        ffmpeg_opts = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn",
        }
        fuente_audio = discord.FFmpegPCMAudio(stream_url, **ffmpeg_opts)
        voz.play(
            fuente_audio,
            after=lambda e: ctx.bot.loop.create_task(reproducir_siguiente(ctx, voz)),
        )
        voz.source = discord.PCMVolumeTransformer(voz.source)
        voz.source.volume = 0.10

        await ctx.send(f"🎶 Reproduciendo **{titulo}**.")
    else:
        await ctx.send("La lista de reproducción ha terminado.")


async def mover(ctx, posicion_actual: int, nueva_posicion: int):
    if 1 <= posicion_actual <= len(playlist) and 1 <= nueva_posicion <= len(playlist):
        cancion = playlist[posicion_actual - 1]
        playlist.remove(cancion)
        playlist.insert(nueva_posicion - 1, cancion)
        await ctx.send(
            f"🎵 Canción **{cancion[0]}** movida a la posición {nueva_posicion}."
        )
    else:
        await ctx.send("⚠️ Posiciones inválidas.")


async def eliminar(ctx, posicion: int):
    if 1 <= posicion <= len(playlist):
        cancion = playlist.pop(posicion - 1)
        await ctx.send(f"🗑️ Canción **{cancion[0]}** eliminada de la lista.")
    else:
        await ctx.send("⚠️ Posición inválida.")


async def limpiar(ctx):
    playlist.clear()
    await ctx.send("🗑️ Lista de reproducción vaciada.")
