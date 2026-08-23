from langchain_deepseek import ChatDeepSeek
import os 



class CLasse_agtacoes_llm() :
    def __init__(self):
        self.desencadear_01l()


    def desencadear_01l(self) :
        self.criar_modelo()


    def criar_modelo(self) :
        caminho_ref = r".\senhas\token_deep.txt"
        with open(caminho_ref,"r",encoding="utf-8") as arquivo_tt :
            senha_ref = arquivo_tt.read()
        self.llm = ChatDeepSeek(
            model="deepseek-chat",
            temperature=0.3,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            api_key=senha_ref
            )