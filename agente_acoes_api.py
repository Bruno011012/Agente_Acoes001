import pandas as pd
import random as rd 
import numpy as np 
import yfinance as yf
import os 
import shutil
import re 
from datetime import datetime,timedelta,date
import time
import calendar
import sqlite3



class Classe_api_acoes() :
    def __init__(self) :
        self.desencadear()
    

    def desencadear(self) :
        self.gerar_requisicao()

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
    
    
    def gerar_requisicao(self) :
        caminho_ref = os.path.join(r".\bases_dados\acoes","base_acoes.json")
        caminho_db = os.path.join(r".\bases_dados\acoes","base_acoes.db")
        # Principais empresas: EUA + Brasil + Grandes mundiais
        tickers = [
            # Americanas
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK-B", "JPM", "V",
            
            # Brasileiras
            "PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA", "ABEV3.SA", "WEGE3.SA", "BBAS3.SA",
            
            # Grandes mundiais
            "NESN.SW", "ASML", "SAP", "MC.PA", "SHEL", "TTE",
            "TSM", "BABA", "0700.HK", "TM", "005930.KS"
        ]

        # Baixa os últimos 6 meses com TODAS as colunas
        df_fina0 = yf.download(tickers, period="6mo", auto_adjust=True, progress=False)
        df_fina1 = df_fina0.stack(level=1, future_stack=True).reset_index()
        df_fina1 = df_fina1[["Date", "Ticker", "Open", "High", "Low", "Close", "Volume"]]
        df_fina1 = df_fina1.fillna(0)
        df_fina1["Nome_Empresa"] = df_fina1["Ticker"].map(self.funcao_aux_01)
        print(df_fina1)
        df_fina1.to_json(caminho_ref,orient="records",force_ascii=False,indent=4)
        with sqlite3.connect(caminho_db) as conn :
            df_fina1.to_sql(
                name="acoes",
                con=conn,
                if_exists="replace",
                index=False
            )

    

Classe_api_acoes()
