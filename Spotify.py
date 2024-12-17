import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from Youtube import playlist
from Youtube import reproducir_siguiente

# Configuración de Spotify
sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id="YOUR_CLIENT_ID",
        client_secret="YOUR_CLIENT_SECRET",
    )
)


def obtener_informacion_spotify(url):
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
