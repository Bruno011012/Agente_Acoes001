import pandas as pd 
import os 
import shutil
import re 
from functools import partial
from toolz import compose,compose_left
from langchain.tools import tool
from agente_acoes_nlp import CLasse_agtacoes_nlp


class CLasse_agtacoes_tools() :
    def __init__(self):
        self.desencadear()


    def desencadear(self) :
        self.criar_parametros()


    def criar_parametros(self) :
        self.classe_nlp = CLasse_agtacoes_nlp()



    def ferramenta_busca_noticias(self,query) :
        funcao_noti = partial(self.classe_nlp.desencadear,query=query)
        @tool
        def tool_noticias(query) :
            """Ferramenta de noticias"""
            print(f"Tokens retornados Noticias {len(funcao_noti())}")
            return funcao_noti()
        return [tool_noticias]


    def ferramenta_busca_empresas(self,query) :
        funcao_noti = partial(self.classe_nlp.desencadear_01,query=query)
        @tool
        def tool_empresas(query) :
            """Ferramenta de empresas"""
            print(f"Tokens retornados Empresas {len(funcao_noti())}")
            return funcao_noti()
        return [tool_empresas]





