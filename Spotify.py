import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from Youtube import playlist
from Youtube import reproducir_siguiente
import asyncio
import credenciales

# Configuración de Spotify
sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=credenciales.SPOTIFY_CLIENT_ID,  # Usar la variable cargada
        client_secret=credenciales.SPOTIFY_CLIENT_SECRET,  # Usar la variable cargada
    )
)


def obtener_informacion_spotify(url: str):
    if "track" in url:
        track = sp.track(url)
        titulo = track["name"]
        artistas = ", ".join(artista["name"] for artista in track["artists"])
        return [f"{titulo} - {artistas}"]
    elif "playlist" in url:
        playlist = sp.playlist(url)
        canciones = [
            f"{item['track']['name']} - {', '.join(artist['name'] for artist in item['track']['artists'])}"
            for item in playlist["tracks"]["items"]
        ]
        return canciones
    else:
        return None
