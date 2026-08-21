from fastapi import FastAPI
import requests


caminho_txt = r".\senhas\token_tlg.txt"
with open(caminho_txt,"r",encoding="utf-8") as arquivo_tt :
    senha_t = arquivo_tt.read().strip()

    
app = FastAPI()

TOKEN = senha_t


@app.get("/")
def home():
    return {"status": "ok"}


@app.post("/webhook")
async def webhook(data: dict):

    print("Update recebido:", data)

    # Verifica se existe uma mensagem
    if "message" not in data:
        return {"status": "ignored"}

    message = data["message"]

    # Verifica se a mensagem possui texto
    if "text" not in message:
        return {"status": "ignored"}

    mensagem = message["text"]
    chat_id = message["chat"]["id"]

    print("Mensagem recebida:", mensagem)

    resposta = f"Você disse: {mensagem}"

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    response = requests.post(
        url,
        json={
            "chat_id": chat_id,
            "text": resposta
        }
    )

    print("Resposta do Telegram:", response.json())

    return {"status": "ok"}