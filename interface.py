import tkinter as tk
from tkinter import Label, Canvas
from datetime import datetime
import pytz
import requests
import threading
import time
import re
from flask import Flask, request, jsonify

# Configuração do Flask para receber falas do assistente
app = Flask(__name__)
fala_atual = ""
falando = False  # Variável global para controlar se o assistente está falando

@app.route("/fala", methods=["POST"])
def receber_fala():
    global falando
    data = request.get_json()
    falando = True  # Ativa a animação da bola
    threading.Thread(target=desativar_fala_apos_tempo).start()
    return jsonify({"status": "ok"})

def desativar_fala_apos_tempo():
    """ Desativa a fala após um tempo baseado no tamanho do texto """
    global falando
    time.sleep(2)  # Tempo fixo de 2 segundos para a animação
    falando = False

# Função para obter a previsão do tempo
def obter_clima_serra():
    api_key = "a000864c59a8bf5f3e388a28e334ae72"
    cidade = "Vitoria"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={api_key}&lang=pt_br&units=metric"
    try:
        resposta = requests.get(url)
        dados = resposta.json()
        return f"{dados['main']['temp']}°C" if resposta.status_code == 200 else "Erro no clima"
    except:
        return "Erro ao acessar API"

# Função para obter notícias
def obter_noticias():
    url = "https://g1.globo.com/dynamo/tecnologia/rss2.xml"
    try:
        resposta = requests.get(url)
        dados = resposta.text
        noticias = dados.split("<item>")
        return [re.sub(r'<.*?>', '', item.split("<title>")[1].split("</title>")[0]) for item in noticias[1:4]]
    except:
        return ["Erro ao acessar notícias"]

# Função para determinar a mensagem conforme o horário
def obter_mensagem_horario():
    hora_atual = datetime.now(pytz.timezone("America/Sao_Paulo")).hour
    if 5 <= hora_atual < 12:
        return "Bom dia! Como posso te ajudar?"
    elif 12 <= hora_atual < 18:
        return "Boa tarde! O que deseja saber?"
    else:
        return "Boa noite! Precisa de algo?"

# Atualiza o relógio
def atualizar_relogio(label):
    while True:
        label.config(text=datetime.now(pytz.timezone("America/Sao_Paulo")).strftime('%H:%M:%S'))
        time.sleep(1)

# Atualiza notícias
def atualizar_noticias(label):
    while True:
        for noticia in obter_noticias():
            label.config(text=noticia)
            time.sleep(10)

# Atualiza temperatura
def atualizar_clima(label):
    while True:
        label.config(text=obter_clima_serra(), font=("Helvetica", 60, "bold"))
        time.sleep(300)

# Atualiza mensagem conforme horário
def atualizar_mensagem(label):
    while True:
        label.config(text=obter_mensagem_horario())
        time.sleep(60)  # Atualiza a cada minuto

# Anima a bola conforme o estado da fala
def animar_fala(canvas):
    global falando
    while True:
        if falando:
            for i in range(3, 12, 2):
                canvas.delete("all")
                canvas.create_oval(50-i, 50-i, 150+i, 150+i, fill="white", outline="white", width=3)
                time.sleep(0.05)
            for i in range(12, 3, -2):
                canvas.delete("all")
                canvas.create_oval(50-i, 50-i, 150+i, 150+i, fill="white", outline="white", width=3)
                time.sleep(0.05)
        else:
            canvas.delete("all")
            canvas.create_oval(50, 50, 150, 150, outline="white", width=3)
        time.sleep(0.1)

# Cria a interface
def criar_interface():
    root = tk.Tk()
    root.title("Assistente Pessoal")
    root.geometry("1920x1080")
    root.configure(bg='black')

    time_label = Label(root, text="", fg="white", bg="black", font=("Helvetica", 40, "bold"))
    time_label.place(relx=0.05, rely=0.1, anchor="w")

    clima_label = Label(root, text="Aguardando clima...", fg="white", bg="black", font=("Helvetica", 60, "bold"))
    clima_label.place(relx=0.95, rely=0.1, anchor="ne")

    noticias_label = Label(root, text="Aguardando notícias...", fg="white", bg="black", font=("Helvetica", 18), wraplength=1400)
    noticias_label.place(relx=0.5, rely=0.85, anchor="center")

    mensagem_label = Label(root, text=obter_mensagem_horario(), fg="white", bg="black", font=("Helvetica", 40, "bold"))
    mensagem_label.place(relx=0.5, rely=0.5, anchor="center")

    canvas = Canvas(root, width=200, height=200, bg="black", highlightthickness=0)
    canvas.place(relx=0.5, rely=0.7, anchor="center")

    threading.Thread(target=atualizar_relogio, args=(time_label,), daemon=True).start()
    threading.Thread(target=atualizar_clima, args=(clima_label,), daemon=True).start()
    threading.Thread(target=atualizar_noticias, args=(noticias_label,), daemon=True).start()
    threading.Thread(target=animar_fala, args=(canvas,), daemon=True).start()
    threading.Thread(target=atualizar_mensagem, args=(mensagem_label,), daemon=True).start()
    threading.Thread(target=lambda: app.run(port=5002, debug=False, use_reloader=False), daemon=True).start()

    root.mainloop()

if __name__ == "__main__":
    criar_interface()
