from fastapi import FastAPI, BackgroundTasks
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
        async def webhook(data: dict, background_tasks: BackgroundTasks):

            # Processa depois de responder ao Telegram
            background_tasks.add_task(
                self.processar_webhook,
                data
            )

            # Responde imediatamente
            return {"status": "ok"}

    def processar_webhook(self, data: dict):

        print("Update recebido:", data)

        if "message" not in data:
            return

        message = data["message"]

        if "text" not in message:
            return

        mensagem = message["text"]
        chat_id = message["chat"]["id"]

        print("Mensagem recebida:", mensagem)

        self.enviar_mensagem(
            chat_id,
            mensagem
        )

    def enviar_documento(
        self,
        chat_id: int,
        caminho_arquivo: str,
        legenda: str = None
    ):

        if not os.path.exists(caminho_arquivo):
            print(f"Arquivo não encontrado: {caminho_arquivo}")
            return None

        url = f"https://api.telegram.org/bot{self.token}/sendDocument"

        with open(caminho_arquivo, "rb") as arquivo:

            files = {
                "document": (
                    os.path.basename(caminho_arquivo),
                    arquivo
                )
            }

            data = {
                "chat_id": chat_id
            }

            if legenda:
                data["caption"] = legenda

            response = requests.post(
                url,
                data=data,
                files=files,
                timeout=120
            )

        print(
            "Resposta do Telegram (documento):",
            response.json()
        )

    def enviar_mensagem(self, chat_id: int, texto: str):

        caminho_ref = r".\zips\analises_ml.zip"

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"

        # 1. Mensagem de carregamento
        response_loading = requests.post(
            url,
            json={
                "chat_id": chat_id,
                "text": "🤖 Criando análise, aguarde..."
            },
            timeout=30
        )

        print(
            "Mensagem de carregamento enviada:",
            response_loading.json()
        )

        # 2. Processa
        try:

            resposta = CLasse_agtacoes_ge01(texto)
            noticias_01 = resposta.desencadear()

        except Exception as erro:

            print("Erro no agente:", erro)

            requests.post(
                url,
                json={
                    "chat_id": chat_id,
                    "text": f"❌ Erro ao criar análise: {erro}"
                },
                timeout=30
            )

            return

        # 3. Resultado
        response = requests.post(
            url,
            json={
                "chat_id": chat_id,
                "text": str(noticias_01)
            },
            timeout=30
        )

        print(
            "Resposta do Telegram:",
            response.json()
        )

        # 4. Documento
        self.enviar_documento(
            chat_id,
            caminho_ref,
            "Analises Machine Learning"
        )


# Instância do bot
bot = TelegramBot()

app = bot.app