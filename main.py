import time
import re
from reconhecimento import ouvir_comando
from emocao import detectar_emocao, gerar_mensagem
from audio import gerar_audio
from chat import responder
from spotify import tocar_musica
from noticias import buscar_noticias_g1, formatar_noticias_para_voz
from clima import obter_previsao_tempo  # Importação do módulo de clima

def extrair_musica_artista(comando):
    """Extrai o nome da música e do artista do comando de voz."""
    padrao = re.search(r"tocar\s+(.*?)\s+de\s+(.*)", comando, re.IGNORECASE)
    
    if padrao:
        musica = padrao.group(1).strip()
        artista = padrao.group(2).strip()
        return musica, artista
    else:
        musica = comando.replace("tocar", "").strip()
        return musica, None

def extrair_cidade_clima(comando):
    """Extrai o nome da cidade do comando de clima"""
    # Padrões para capturar "tempo em [cidade]", "clima em [cidade]", etc.
    padroes = [
        r"(?:tempo|clima|previsão)\s+(?:em|na|no|para)?\s*([\w\s]+)",
        r"(?:qual|como)\s+(?:é|está)\s+o\s+(?:tempo|clima)\s+(?:em|na|no)?\s*([\w\s]+)"
    ]
    
    for padrao in padroes:
        match = re.search(padrao, comando, re.IGNORECASE)
        if match:
            cidade = match.group(1).strip()
            # Remove palavras desnecessárias no final
            cidade = re.sub(r'\s+(?:do|da|de|dos|das)$', '', cidade, flags=re.IGNORECASE)
            return cidade
    
    return None

def modo_assistente():
    print("Assistente ativado! Diga 'espelho' para iniciar.")
    categorias_validas = ['tecnologia', 'política', 'economia', 'mundo', 'saúde', 
                        'educação', 'carros', 'ciência', 'emprego', 'loterias',
                        'música', 'natureza', 'bizarro', 'arte', 'games', 'viagem']

    while True:
        print("Aguardando comando...")
        comando = ouvir_comando()

        if comando and "espelho" in comando.lower():
            print("Assistente pronto! Faça sua pergunta.")
            gerar_audio("Estou ouvindo.")

            while True:
                print("Aguardando comando...")
                comando = ouvir_comando()

                if not comando:
                    continue

                comando = comando.lower()

                if comando == "sair":
                    print("Voltando ao modo de espera...")
                    gerar_audio("Voltando ao modo de espera.")
                    break

                elif comando.startswith("tocar"):
                    musica, artista = extrair_musica_artista(comando)
                    if musica:
                        print(f"Procurando por {musica}...")
                        resultado = tocar_musica(musica, artista)
                        if resultado:
                            gerar_audio(f"Tocando {musica}")
                        else:
                            gerar_audio(f"Não encontrei {musica}")
                    else:
                        gerar_audio("Diga o nome da música")

                elif "notícias" in comando or "noticias" in comando:
                    print("Processando notícias...")
                    
                    categoria = None
                    for cat in categorias_validas:
                        if cat in comando:
                            categoria = cat
                            break
                    
                    padrao = re.search(r"not[íi]cias (?:sobre|de) (.+)", comando)
                    termo = padrao.group(1).strip() if padrao else None
                    
                    if termo and not categoria:
                        gerar_audio(f"Buscando notícias sobre {termo}")
                        noticias = buscar_noticias_g1(termo=termo)
                    elif categoria:
                        gerar_audio(f"Buscando notícias de {categoria}")
                        noticias = buscar_noticias_g1(categoria=categoria)
                    else:
                        gerar_audio("Buscando principais notícias")
                        noticias = buscar_noticias_g1()
                    
                    textos = formatar_noticias_para_voz(noticias[:3])
                    
                    for texto in textos:
                        print(f"- {texto}")
                        gerar_audio(texto)
                        time.sleep(1)

                elif "tempo" in comando or "clima" in comando or "previsão" in comando:
                    cidade = extrair_cidade_clima(comando)
                    
                    if cidade:
                        print(f"Buscando clima para {cidade}...")
                        previsao = obter_previsao_tempo(cidade)
                    else:
                        gerar_audio("Para qual cidade você quer a previsão?")
                        cidade = ouvir_comando()
                        if cidade:
                            print(f"Buscando clima para {cidade}...")
                            previsao = obter_previsao_tempo(cidade)
                        else:
                            cidade = "Vitoria"
                            gerar_audio("Buscando previsão para Vitória")
                            previsao = obter_previsao_tempo(cidade)
                    
                    print(f"Clima: {previsao}")
                    gerar_audio(previsao)

                elif comando == "analisar":
                    emocao = detectar_emocao()
                    mensagem = gerar_mensagem(emocao)
                    print(f"Assistente: {mensagem}")
                    gerar_audio(mensagem)

                else:
                    resposta = responder(comando, "neutral")
                    print(f"Assistente: {resposta}")
                    gerar_audio(resposta)

if __name__ == "__main__":
    modo_assistente()