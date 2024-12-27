from discord.utils import get
from collections import deque
import yt_dlp as youtube_dl
import discord
import credenciales
from googleapiclient.discovery import build

YOUTUBE_API_KEY = credenciales.YOUTUBE_API_KEY


playlist = deque()  # Cola global para la lista de reproducción


async def reproducir(ctx, bot, url, track_name=None):
    global playlist
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

    if track_name != None:
        print(track_name)
        playlist.append((track_name, url))
        await ctx.send(f"🎶 Se añadió **{track_name}** a la lista.")
    else:
        print(f"{titulo}")
        playlist.append((titulo, url))
        await ctx.send(f"🎶 Se añadió **{titulo}** a la lista.")

    if not voz.is_playing():
        await reproducir_siguiente(ctx, voz)


async def buscar_youtube(query):
    global playlist
    """
    Busca en YouTube y devuelve el título y URL del primer resultado.
    """
    opciones = {
        "quiet": True,
        "format": "bestaudio/best",
        "noplaylist": True,
    }
    with youtube_dl.YoutubeDL(opciones) as ydl:
        try:
            resultados = ydl.extract_info(f"ytsearch:{query}", download=False)[
                "entries"
            ]
            if resultados:
                return resultados[0]["title"], resultados[0]["url"]
        except Exception as e:
            print(f"Error buscando en YouTube: {e}")
            return None, None


async def buscar_query(query):
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    request = youtube.search().list(part="snippet", maxResults=1, q=query, type="video")
    response = request.execute()
    if response["items"]:
        video_id = response["items"][0]["id"]["videoId"]
        titulo = response["items"][0]["snippet"]["title"]
        url = f"https://www.youtube.com/watch?v={video_id}"
        return titulo, url
    else:
        return None, None


async def reproducir_siguiente(ctx, voz):
    global playlist
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
        # await ctx.send(url)
    else:
        await ctx.send("La lista de reproducción ha terminado.")


# ---------------------------------------------------------------------------------------------
