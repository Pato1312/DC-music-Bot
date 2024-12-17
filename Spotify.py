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
        canciones = []
        for item in playlist["tracks"]["items"]:
            track = item["track"]
            titulo = track["name"]
            artistas = ", ".join(artista["name"] for artista in track["artists"])
            canciones.append(f"{titulo} - {artistas}")
        return canciones

    elif "album" in url:
        # Procesa un enlace de un álbum
        album = sp.album(url)
        canciones = [
            f"{track['name']} - {', '.join(artist['name'] for artist in track['artists'])}"
            for track in album.get("tracks", {}).get("items", [])
        ]
        return canciones

    else:
        return None
