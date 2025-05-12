import os
from dotenv import load_dotenv

load_dotenv()

# Chave da API OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Credenciais do Spotify
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "localhost:3000")


# Escopo de permissões do Spotify
SPOTIFY_SCOPE = "user-modify-playback-state user-read-playback-state user-read-currently-playing"
