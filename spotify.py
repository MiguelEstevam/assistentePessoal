import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import logging

# Configuração do logging
logging.basicConfig(level=logging.INFO)

# Carrega as variáveis de ambiente do .env
load_dotenv()

# Configuração do SpotifyOAuth
sp_oauth = SpotifyOAuth(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
    scope="user-modify-playback-state user-read-playback-state"
)

def get_spotify_client():
    """Obtém o cliente autenticado do Spotify e renova o token se necessário."""
    token_info = sp_oauth.get_cached_token()

    if not token_info:
        logging.error("Erro: Nenhum token disponível. Faça login novamente.")
        return None

    # Se o token expirou, renova automaticamente
    if sp_oauth.is_token_expired(token_info):
        logging.info("Token expirado. Renovando...")
        token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])

    return spotipy.Spotify(auth=token_info["access_token"])

def tocar_musica(musica, artista=None):
    """Pesquisa e toca uma música no Spotify."""
    sp = get_spotify_client()
    if not sp:
        logging.error("Erro: Spotify não autenticado.")
        return False

    query = f"track:{musica}"
    if artista:
        query += f" artist:{artista}"
    
    results = sp.search(q=query, limit=1, type="track")
    if results["tracks"]["items"]:
        track = results["tracks"]["items"][0]
        uri = track["uri"]
        logging.info(f"Tocando: {track['name']} - {track['artists'][0]['name']}")

        devices = sp.devices()
        if devices["devices"]:
            device_id = devices["devices"][0]["id"]
            sp.start_playback(device_id=device_id, uris=[uri])
            return True
        else:
            logging.warning("Nenhum dispositivo ativo encontrado.")
            return False
    else:
        logging.warning(f"Música '{musica}' não encontrada.")
        return False
