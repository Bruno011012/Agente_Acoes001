import pandas as pd 
import random as rd 
import numpy as np 
from functools import partial
from toolz import compose,compose_left
import os 
import shutil
import re 
import sqlite3


class CLasse_agtacoes_q() :
    def __init__(self) :
        self.desencadear()


    def desencadear(self) :
        self.criar_parametros()


    def funcao_aux_01(self,x):
        ticker_para_nome = {
            # Americanas
            "AAPL": "Apple",
            "MSFT": "Microsoft",
            "GOOGL": "Google",
            "AMZN": "Amazon",
            "NVDA": "NVIDIA",
            "META": "Meta Platforms",
            "TSLA": "Tesla",
            "BRK-B": "Berkshire Hathaway",
            "JPM": "JPMorgan Chase",
            "V": "Visa",

            # Brasileiras
            "PETR4.SA": "Petrobras",
            "VALE3.SA": "Vale",
            "ITUB4.SA": "Itaú Unibanco",
            "BBDC4.SA": "Bradesco",
            "ABEV3.SA": "Ambev",
            "WEGE3.SA": "WEG",
            "BBAS3.SA": "Banco do Brasil",

            # Grandes mundiais
            "NESN.SW": "Nestlé",
            "ASML": "ASML Holding",
            "SAP": "SAP",
            "MC.PA": "LVMH",
            "SHEL": "Shell",
            "TTE": "TotalEnergies",
            "TSM": "TSMC",
            "BABA": "Alibaba",
            "0700.HK": "Tencent",
            "TM": "Toyota",
            "005930.KS": "Samsung Electronics"
        }
        return ticker_para_nome[x]


    
    def criar_parametros(self) :
        caminho = r".\data\acoes\base_acoes.db"
        self.conexao = sqlite3.connect(caminho)


    def tabela_acoes_total(self,emp_ref)-> pd.DataFrame :
        query = f"""
                SELECT * FROM acoes WHERE Open <> 0 AND Ticker = '{emp_ref}' 
                """
        frame_tr = pd.DataFrame(pd.read_sql_query(query,self.conexao))
        return frame_tr



    def tabela_acoes(self,emp_ref,data_i0,data_f0)-> pd.DataFrame :
        query = f"""
                SELECT * FROM acoes WHERE Open <> 0 AND Ticker = '{emp_ref}' AND Date >= '{data_i0}' AND Date <= '{data_f0}'
                """
        frame_tr = pd.DataFrame(pd.read_sql_query(query,self.conexao))
        return frame_tr



CLasse_agtacoes_q()