import speech_recognition as sr

recognizer = sr.Recognizer()

def ouvir_comando():
    """ Captura o comando de voz do usuário """
    with sr.Microphone() as source:
        print("Aguardando comando...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=10)
            comando = recognizer.recognize_google(audio, language="pt-BR").lower()
            print(f"Você disse: {comando}")
            return comando
        except sr.WaitTimeoutError:
            print("Nenhum comando detectado.")
        except sr.UnknownValueError:
            print("Não entendi. Tente novamente.")
        except sr.RequestError:
            print("Erro ao acessar o serviço de reconhecimento de voz.")
    return None
