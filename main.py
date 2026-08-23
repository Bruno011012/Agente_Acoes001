from fastapi import FastAPI
import requests
from agente_acoes_ge01 import CLasse_agtacoes_ge01
import os 



class TelegramBot:
    def __init__(self, token_path: str = r".\senhas\token_tlg.txt"):
        with open(token_path, "r", encoding="utf-8") as arquivo:
            self.token = arquivo.read().strip()

        self.app = FastAPI()
        self._registrar_rotas()

    def _registrar_rotas(self):
        @self.app.get("/")
        def home():
            return {"status": "ok"}

        @self.app.post("/webhook")
        async def webhook(data: dict):
            return await self.processar_webhook(data)

    async def processar_webhook(self, data: dict):
        print("Update recebido:", data)

        if "message" not in data:
            return {"status": "ignored"}

        message = data["message"]

        if "text" not in message:
            return {"status": "ignored"}

        mensagem = message["text"]
        chat_id = message["chat"]["id"]

        print("Mensagem recebida:", mensagem)

        resposta = f"Você disse: {mensagem}"
        self.enviar_mensagem(chat_id, resposta)

        return {"status": "ok"}

    def enviar_documento(self, chat_id: int, caminho_arquivo: str, legenda: str = None):
        """
        Envia um arquivo (zip, pdf, etc.) para o Telegram.
        """
        if not os.path.exists(caminho_arquivo):
            print(f"Arquivo não encontrado: {caminho_arquivo}")
            return None

        url = f"https://api.telegram.org/bot{self.token}/sendDocument"

        with open(caminho_arquivo, "rb") as arquivo:
            files = {
                "document": (os.path.basename(caminho_arquivo), arquivo)
            }
            data = {
                "chat_id": chat_id
            }
            if legenda:
                data["caption"] = legenda

            response = requests.post(url, data=data, files=files)

        print("Resposta do Telegram (documento):", response.json())

    

    def enviar_mensagem(self, chat_id: int, texto: str):
        caminho_ref = r".\zips\analises_ml.zip"
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"

        # 1. Envia mensagem de carregamento
        response_loading = requests.post(
            url,
            json={
                "chat_id": chat_id,
                "text": "🤖 Criando análise, aguarde..."
            }
        )
        print("Mensagem de carregamento enviada:", response_loading.json())

        # 2. Processa a análise (pode demorar)
        resposta = CLasse_agtacoes_ge01(texto)
        noticias_01 = resposta.desencadear()

        # 3. Envia o resultado final
        response = requests.post(
            url,
            json={
                "chat_id": chat_id,
                "text": noticias_01
            }
        )
        print("Resposta do Telegram:", response.json())

        # 4. Envia o documento
        self.enviar_documento(chat_id, caminho_ref, "Analises Machine Learning")



# Instância do bot
bot = TelegramBot()
app = bot.app