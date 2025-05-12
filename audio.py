import openai
import pygame
import os
import time
import requests
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def gerar_audio(texto):
    """Gera áudio usando OpenAI TTS e envia o texto para a interface."""
    
    # Envia o texto para a interface antes de reproduzir o áudio
    try:
        requests.post("http://127.0.0.1:5002/fala", json={"texto": texto})
    except requests.exceptions.RequestException as e:
        print(f"⚠ Erro ao enviar fala para a interface: {e}")
    
    try:
        response = openai.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=texto
        )

        filename = "resposta.mp3"

        with open(filename, "wb") as f:
            f.write(response.content)

        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

        pygame.mixer.quit()
        
        # Remove o arquivo após reprodução
        try:
            os.remove(filename)
        except OSError as e:
            print(f"⚠ Erro ao remover arquivo de áudio: {e}")

    except Exception as e:
        print(f"⚠ Erro ao gerar ou reproduzir áudio: {e}")
