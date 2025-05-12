from flask import Flask, request, redirect, session, jsonify
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import logging
from dotenv import load_dotenv

# Configuração do logging
logging.basicConfig(level=logging.INFO)

# Carrega as variáveis de ambiente
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
app.config['SESSION_COOKIE_NAME'] = 'Spotify-Login'

sp_oauth = SpotifyOAuth(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
    scope="user-modify-playback-state user-read-playback-state"
)

def get_token():
    """Obtém o token do Spotify e o atualiza se necessário."""
    token_info = session.get("token_info", None)
    
    if not token_info:
        logging.error("Erro: Nenhum token disponível. Faça login novamente.")
        return None

    # Verifica se o token expirou
    if sp_oauth.is_token_expired(token_info):
        logging.info("Token expirado. Renovando...")
        token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])
        session["token_info"] = token_info

    return token_info["access_token"]

@app.route("/login")
def login():
    """Redireciona para autenticação do Spotify."""
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route("/callback")
def callback():
    """Lida com a resposta do Spotify após autenticação."""
    code = request.args.get("code")
    token_info = sp_oauth.get_access_token(code, as_dict=True)
    session["token_info"] = token_info
    return "Login bem-sucedido! Você pode fechar esta aba."

@app.route("/play")
def play():
    """Toca uma música com base no nome passado na URL."""
    access_token = get_token()
    if not access_token:
        return jsonify({"error": "Spotify não autenticado"}), 401

    sp = spotipy.Spotify(auth=access_token)
    musica = request.args.get("musica")
    artista = request.args.get("artista", None)

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
            return jsonify({"message": f"Tocando {track['name']}"}), 200
        else:
            return jsonify({"error": "Nenhum dispositivo ativo encontrado"}), 400
    else:
        return jsonify({"error": f"Música '{musica}' não encontrada"}), 404

if __name__ == "__main__":
    app.run(debug=True)
