import requests
from dotenv import load_dotenv
import os
from datetime import datetime
import re

load_dotenv()

def normalizar_nome_cidade(cidade):
    """Normaliza o nome da cidade para melhor busca na API"""
    # Remove expressões comuns que atrapalham a busca
    cidade = re.sub(r'\b(?:cidade|munic[ií]pio|distrito)\b', '', cidade, flags=re.IGNORECASE)
    cidade = re.sub(r'[^a-zA-ZÀ-ÿ\s]', '', cidade)  # Mantém apenas letras e espaços
    cidade = cidade.strip()
    
    # Corrige nomes comuns de cidades
    correcoes = {
        'sao paulo': 'São Paulo',
        'rio de janeiro': 'Rio de Janeiro',
        'belem': 'Belém',
        'para': 'Belém',  # Para evitar confusão com o estado
        'espirito santo': 'Vitória',
        'vix': 'Vitória',
        'floripa': 'Florianópolis'
    }
    
    return correcoes.get(cidade.lower(), cidade)

def obter_coordenadas(cidade, api_key):
    """Obtém as coordenadas geográficas para uma cidade"""
    try:
        cidade_normalizada = normalizar_nome_cidade(cidade)
        url = f"http://api.openweathermap.org/geo/1.0/direct?q={cidade_normalizada}&limit=5&appid={api_key}"
        resposta = requests.get(url, timeout=10)
        dados = resposta.json()
        
        if not dados:
            # Tenta sem acentos e caracteres especiais
            cidade_simples = re.sub(r'[^a-zA-Z\s]', '', cidade_normalizada)
            url = f"http://api.openweathermap.org/geo/1.0/direct?q={cidade_simples}&limit=5&appid={api_key}"
            resposta = requests.get(url, timeout=10)
            dados = resposta.json()
            if not dados:
                return None

        # Prioriza resultados no Brasil
        for resultado in dados:
            if resultado.get('country') == 'BR':
                return {
                    'lat': resultado['lat'],
                    'lon': resultado['lon'],
                    'nome': resultado.get('name', cidade),
                    'estado': resultado.get('state', '')
                }
        
        # Se não encontrar no BR, retorna o primeiro resultado
        return {
            'lat': dados[0]['lat'],
            'lon': dados[0]['lon'],
            'nome': dados[0].get('name', cidade),
            'estado': dados[0].get('state', '')
        }
    
    except Exception as e:
        print(f"Erro ao obter coordenadas: {e}")
        return None

def obter_previsao_tempo(cidade):
    """Obtém a previsão do tempo para uma cidade usando a API do OpenWeatherMap"""
    API_KEY = os.getenv("OPENWEATHER_API_KEY")
    if not API_KEY:
        return "Erro: Chave da API OpenWeather não configurada. Configure sua chave no arquivo .env"
    
    # Primeiro obtém as coordenadas
    coordenadas = obter_coordenadas(cidade, API_KEY)
    if not coordenadas:
        return f"Não consegui encontrar a cidade {cidade}. Por favor, tente novamente com o nome completo da cidade."
    
    try:
        # Obtém a previsão atual
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={coordenadas['lat']}&lon={coordenadas['lon']}&appid={API_KEY}&lang=pt_br&units=metric"
        resposta = requests.get(url, timeout=10)
        dados = resposta.json()
        
        # Processa os dados principais
        temperatura = dados['main']['temp']
        descricao = dados['weather'][0]['description'].capitalize()
        umidade = dados['main']['humidity']
        vento = dados['wind']['speed'] * 3.6  # Converte m/s para km/h
        pressao = dados['main']['pressure']
        
        # Processa dados opcionais
        sensacao = dados['main'].get('feels_like', temperatura)
        visibilidade = dados.get('visibility', 'não disponível')
        if isinstance(visibilidade, int):
            visibilidade = f"{visibilidade/1000:.1f} km" if visibilidade >= 1000 else f"{visibilidade} metros"
        
        # Formata a mensagem
        localizacao = f"{coordenadas['nome']}"
        if coordenadas['estado']:
            localizacao += f", {coordenadas['estado']}"
        
        mensagem = (
            f"Previsão para {localizacao}: {descricao}. "
            f"Temperatura: {temperatura:.1f}°C (sensação de {sensacao:.1f}°C). "
            f"Umidade: {umidade}%. Vento: {vento:.1f} km/h. "
            f"Pressão atmosférica: {pressao} hPa. "
            f"Visibilidade: {visibilidade}."
        )
        
        return mensagem
    
    except KeyError as e:
        print(f"Erro ao processar dados da API: {e}")
        return "Houve um erro ao processar os dados meteorológicos."
    except Exception as e:
        print(f"Erro ao obter previsão: {e}")
        return "Não consegui obter a previsão do tempo no momento. Por favor, tente novamente mais tarde."

def obter_previsao_extendida(cidade, dias=3):
    """Obtém previsão extendida (requer assinatura paga da API)"""
    return "A previsão extendida requer uma assinatura paga da API OpenWeather."