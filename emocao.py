import cv2
import random
from deepface import DeepFace

def detectar_emocao():
    """ Captura um frame da câmera e analisa a emoção facial """
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    
    if ret:
        try:
            resultado = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
            emocao = resultado[0]['dominant_emotion']
            print(f"Emoção detectada: {emocao}")
            return emocao
        except Exception as e:
            print(f"Erro na detecção de emoção: {e}")
    
    return "neutral"

def gerar_mensagem(emocao):
    """ Gera uma frase aleatória baseada na emoção detectada """
    frases = {
        "happy": [
            "Vejo que você está feliz! Continue espalhando essa alegria!",
            "Que bom te ver sorrindo! Espero que seu dia continue incrível!",
            "A felicidade fica ótima em você! Aproveite cada momento!"
        ],
        "sad": [
            "Percebo que você está triste. Se precisar de alguém para conversar, estou aqui.",
            "Tudo bem se sentir assim. O importante é saber que momentos difíceis passam.",
            "Sei que pode estar sendo um dia difícil, mas coisas boas estão por vir."
        ],
        "angry": [
            "Você parece irritado. Que tal uma pausa para respirar fundo?",
            "Tente focar no que está ao seu controle. O resto pode esperar.",
            "Às vezes, dar um passo para trás ajuda a enxergar a situação melhor."
        ],
        "neutral": [
            "Você está com uma expressão neutra. Que tal fazer algo divertido?",
            "Nem feliz, nem triste... talvez um café ou uma pausa te anime?",
            "O dia parece normal, mas sempre há espaço para uma pequena aventura!"
        ]
    }

    return random.choice(frases.get(emocao, ["Espero que você esteja bem!"]))
