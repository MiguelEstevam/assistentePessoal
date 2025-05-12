import re
from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)  # Novo cliente da SDK v1.0+

def remover_links_e_sites(texto):
    """Remove links completos e referências de sites/domínios do texto"""
    # Remove links
    texto_sem_links = re.sub(r'http[s]?://\S+', '', texto)
    # Remove nomes de sites ou domínios (exemplo: espndeportes.espn.com)
    texto_sem_sites = re.sub(r'\([a-zA-Z0-9.-]+\)', '', texto_sem_links)
    return texto_sem_sites.strip()

def responder(pergunta, emocao):
    """Envia a pergunta para a OpenAI com busca na web e remove links e sites da resposta"""
    prompt = f"Usuário parece {emocao}. Responda de forma apropriada. Pergunta: {pergunta}"

    try:
        resposta = client.chat.completions.create(
            model="gpt-4o-search-preview",
            web_search_options={},
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        conteudo = resposta.choices[0].message.content.strip()
        return remover_links_e_sites(conteudo)
    except Exception as e:
        print(f"Erro ao obter resposta: {e}")
        return "Desculpe, ocorreu um erro."
