import feedparser
import requests
import re
from urllib.parse import quote

# Mapeamento de categorias para URLs RSS
CATEGORIAS_RSS = {
    'brasil': 'https://g1.globo.com/dynamo/brasil/rss2.xml',
    'carros': 'https://g1.globo.com/dynamo/carros/rss2.xml',
    'ciência': 'https://g1.globo.com/dynamo/ciencia-e-saude/rss2.xml',
    'saúde': 'https://g1.globo.com/dynamo/ciencia-e-saude/rss2.xml',
    'emprego': 'https://g1.globo.com/dynamo/concursos-e-emprego/rss2.xml',
    'economia': 'https://g1.globo.com/dynamo/economia/rss2.xml',
    'educação': 'https://g1.globo.com/dynamo/educacao/rss2.xml',
    'loterias': 'https://g1.globo.com/dynamo/loterias/rss2.xml',
    'mundo': 'https://g1.globo.com/dynamo/mundo/rss2.xml',
    'música': 'https://g1.globo.com/dynamo/musica/rss2.xml',
    'natureza': 'https://g1.globo.com/dynamo/natureza/rss2.xml',
    'bizarro': 'https://g1.globo.com/dynamo/planeta-bizarro/rss2.xml',
    'política': 'https://g1.globo.com/dynamo/politica/mensalao/rss2.xml',
    'arte': 'https://g1.globo.com/dynamo/pop-arte/rss2.xml',
    'tecnologia': 'https://g1.globo.com/dynamo/tecnologia/rss2.xml',
    'games': 'https://g1.globo.com/dynamo/tecnologia/rss2.xml',
    'viagem': 'https://g1.globo.com/dynamo/turismo-e-viagem/rss2.xml'
}

def limpar_texto(texto):
    """Remove tags HTML e conteúdo não desejado do texto"""
    if not texto:
        return ""
    
    # Remove tags HTML
    texto_limpo = re.sub(r'<[^>]+>', '', texto)
    # Remove conteúdo após imagens
    texto_limpo = re.sub(r'<img.*', '', texto_limpo)
    # Remove múltiplos espaços e quebras de linha
    texto_limpo = re.sub(r'\s+', ' ', texto_limpo).strip()
    return texto_limpo

def buscar_noticias_g1(termo=None, categoria=None, max_noticias=3):
    """Busca notícias no G1 usando RSS feeds"""
    try:
        if termo:
            # Busca por termo específico usando a API de busca do G1
            url = f"https://g1.globo.com/busca/?q={quote(termo)}&output=rss"
            feed = feedparser.parse(url)
        elif categoria and categoria.lower() in CATEGORIAS_RSS:
            # Busca por categoria pré-definida
            feed = feedparser.parse(CATEGORIAS_RSS[categoria.lower()])
        else:
            # Notícias principais (usando feed geral do Brasil)
            feed = feedparser.parse(CATEGORIAS_RSS['brasil'])
        
        noticias = []
        for entry in feed.entries[:max_noticias]:
            noticias.append({
                'titulo': limpar_texto(entry.title),
                'resumo': limpar_texto(entry.description) if 'description' in entry else '',
                'link': entry.link,
                'data': entry.published if 'published' in entry else ''
            })
        
        return noticias if noticias else [{
            'titulo': 'Nenhuma notícia encontrada',
            'resumo': '',
            'link': ''
        }]
    
    except Exception as e:
        print(f"Erro ao buscar notícias: {e}")
        return [{
            'titulo': 'Houve um erro ao buscar notícias',
            'resumo': 'Por favor, tente novamente mais tarde',
            'link': ''
        }]

def formatar_noticias_para_voz(noticias):
    """Formata as notícias para serem faladas pelo assistente"""
    if not noticias or noticias[0]['titulo'] == 'Nenhuma notícia encontrada':
        return ["Não encontrei notícias no momento. Por favor, tente mais tarde."]
    
    if noticias[0]['titulo'] == 'Houve um erro ao buscar notícias':
        return ["Desculpe, estou tendo problemas para acessar as notícias. Tente novamente mais tarde."]
    
    textos = []
    for i, noticia in enumerate(noticias, 1):
        texto = f"Notícia {i}: {noticia['titulo']}"
        if noticia['resumo']:
            # Limita o resumo a 150 caracteres para não ficar muito extenso
            resumo = noticia['resumo'][:150] + '...' if len(noticia['resumo']) > 150 else noticia['resumo']
            texto += f". {resumo}"
        textos.append(texto)
    
    return textos