import pandas as pd 
import random as rd 
import numpy as np 
import os
import shutil
import re 
import sqlite3
from functools import partial
from toolz import compose,compose_left
import plotly
from scipy.signal import (
    savgol_filter,find_peaks,correlate,periodogram,butter,filtfilt
)
from sklearn.cluster import KMeans
from agente_acoes_q import CLasse_agtacoes_q
import plotly.express as px 
import webbrowser
from plotly.subplots import make_subplots


class CLasse_agtacoes_analyses() :
    def __init__(self,empr_ref,data_ref0=None,data_ref1=None):
        self.empre_ref = empr_ref
        self.data_ref01 = data_ref0
        self.data_ref02 = data_ref1
        self.funcao_nomeemp001 = partial(self.funcao_aux_empre,x=self.empre_ref)
        self.desencadear()


    def desencadear(self) :
        self.criar_parametros()
        self.conferencia_datas_ini()
        self.carregar_tabela_ori()
        self.criar_subplot_final()

    def funcao_aux_empre(self,x=None) :
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
        return ticker_para_nome[x[0]]


    
    def criar_parametros(self) :
        self.tabelas = CLasse_agtacoes_q()


    def conferencia_datas_ini(self) :
        if self.data_ref01 == None or self.data_ref02 == None :
            self.tipo_cons = 1
        else :
            self.tipo_cons = 0



    def carregar_tabela_ori(self) :
        if self.tipo_cons == 1 :
            frame_tr = self.tabelas.tabela_acoes_total(self.empre_ref)
        else :
            frame_tr = self.tabelas.tabela_acoes(self.empre_ref,self.data_ref01,self.data_ref02)
        frame_tr["Date"] = pd.to_datetime(frame_tr["Date"],errors="coerce").reset_index(drop=True)
        self.frame_tr = frame_tr.copy()
        print(self.frame_tr)


    def criar_subplot_final(self) :
        caminho_grf = r".\graficos\analises_scipy"
        df = self.frame_tr
        # Dados dos gráficos
        df["suavizada"] = savgol_filter(df["Close"], 21, 3)

        picos, _ = find_peaks(df["Close"], prominence=10)

        y = df["Close"].values - df["Close"].mean()
        acf = correlate(y, y, mode="full")
        acf = acf[len(y)-1:] / acf[len(y)-1]
        lags = np.arange(len(acf))

        frequencia, potencia = periodogram(df["Close"])

        b, a = butter(3, 0.1, btype="low")
        df["filtrada"] = filtfilt(b, a, df["Close"])

        df["residuo"] = df["Close"] - df["suavizada"]
        anomalias, _ = find_peaks(
            np.abs(df["residuo"]),
            prominence=10
        )

        # Subplots
        fig = make_subplots(
            rows=3,
            cols=2,
            specs=[
                [{}, {}],
                [{}, {}],
                [{}, {}]
            ],
            subplot_titles=(
                "Tendência Suavizada",
                "Detecção de Picos",
                "Autocorrelação",
                "Espectro de Frequência",
                "Filtro Passa-Baixa",
                "Detecção de Anomalias"
            )
        )

        # 01 - Suavização
        fig.add_scatter(
            x=df["Date"], y=df["Close"],
            name="Close",
            row=1, col=1
        )
        fig.add_scatter(
            x=df["Date"], y=df["suavizada"],
            name="Suavizada",
            row=1, col=1
        )

        # 02 - Picos
        fig.add_scatter(
            x=df["Date"], y=df["Close"],
            name="Close",
            row=1, col=2
        )
        fig.add_scatter(
            x=df.iloc[picos]["Date"],
            y=df.iloc[picos]["Close"],
            mode="markers",
            name="Picos",
            row=1, col=2
        )

        # 03 - Autocorrelação
        fig.add_scatter(
            x=lags,
            y=acf,
            name="ACF",
            row=2, col=1
        )

        # 04 - Frequência
        fig.add_scatter(
            x=frequencia,
            y=potencia,
            name="Potência",
            row=2, col=2
        )

        # 05 - Filtro
        fig.add_scatter(
            x=df["Date"], y=df["Close"],
            name="Close",
            row=3, col=1
        )
        fig.add_scatter(
            x=df["Date"], y=df["filtrada"],
            name="Filtrada",
            row=3, col=1
        )

        # 06 - Anomalias
        fig.add_scatter(
            x=df["Date"], y=df["Close"],
            name="Close",
            row=3, col=2
        )
        fig.add_scatter(
            x=df.iloc[anomalias]["Date"],
            y=df.iloc[anomalias]["Close"],
            mode="markers",
            name="Anomalias",
            row=3, col=2
        )

        fig.update_layout(
            template="plotly_dark",
            height=900,
            title=f"Análises Series Temporais - Série Temporal {self.funcao_nomeemp001()}"
        )

        arquivo_grf = os.path.join(caminho_grf,f"consolidado_{self.funcao_nomeemp001()}.html")
        fig.write_html(arquivo_grf,full_html=True,
            include_plotlyjs=True,
            config={
                "responsive": True
            })
        webbrowser.open(arquivo_grf)


class CLasse_agtacoes_analysesc() :
    def __init__(self,empr_ref,data_ref0=None,data_ref1=None):
        self.empre_ref = empr_ref
        self.data_ref01 = data_ref0
        self.data_ref02 = data_ref1
        self.desencadear()


    def desencadear(self) :
        self.criar_parametros()
        self.conferencia_datas_ini()
        self.carregar_tabela_ori()
        self.criacao_subplots_comp()
    

    def criar_parametros(self) :
        self.tabelas = CLasse_agtacoes_q()


    def conferencia_datas_ini(self) :
        if self.data_ref01 == None or self.data_ref02 == None :
            self.tipo_cons = 1
        else :
            self.tipo_cons = 0



    def carregar_tabela_ori(self) :
        if self.tipo_cons == 1 :
            frame_tr = self.tabelas.tabela_acoes_total(self.empre_ref)
        else :
            frame_tr = self.tabelas.tabela_acoes(self.empre_ref,self.data_ref01,self.data_ref02)
        frame_tr["Date"] = pd.to_datetime(frame_tr["Date"],errors="coerce").reset_index(drop=True)
        self.frame_tr = frame_tr.copy()
        print(self.frame_tr)


    def criacao_subplots_comp(self) :
        # ==========================================================
        # GRÁFICOS
        # ==========================================================

        grafico_01 = px.line(
            self.frame_tr,
            x="Date",
            y="Close",
            color="Empresas",
            markers=True,
            template="plotly_dark"
        )

        grafico_02 = px.histogram(
            self.frame_tr,
            x="Close",
            color="Empresas",
            template="plotly_dark"
        )

        grafico_03 = px.scatter(
            self.frame_tr,
            x="High",
            y="Close",
            color="Empresas",
            trendline="lowess",
            trendline_color_override="red",
            template="plotly_dark"
        )

        grafico_04 = px.scatter_3d(
            self.frame_tr,
            x="Open",
            y="Close",
            z="Volume",
            color="Empresas",
            template="plotly_dark"
        )

        # ==========================================================
        # SUBPLOTS
        # ==========================================================

        fig = make_subplots(

            rows=2,
            cols=2,

            specs=[
                [
                    {"type": "xy"},
                    {"type": "xy"}
                ],
                [
                    {"type": "xy"},
                    {"type": "scene"}
                ]
            ],

            subplot_titles=[
                "Evolução do Close",
                "Distribuição do Close",
                "High × Close",
                "Open × Close × Volume"
            ],

            # Espaçamento mínimo para aproveitar a tela
            horizontal_spacing=0.09,
            vertical_spacing=0.09
        )

        # ==========================================================
        # GRÁFICO 01
        # ==========================================================

        for trace in grafico_01.data:
            fig.add_trace(
                trace,
                row=1,
                col=1
            )

        # ==========================================================
        # GRÁFICO 02
        # ==========================================================

        for trace in grafico_02.data:
            fig.add_trace(
                trace,
                row=1,
                col=2
            )

        # ==========================================================
        # GRÁFICO 03
        # ==========================================================

        for trace in grafico_03.data:
            fig.add_trace(
                trace,
                row=2,
                col=1
            )

        # ==========================================================
        # GRÁFICO 04
        # ==========================================================

        for trace in grafico_04.data:
            fig.add_trace(
                trace,
                row=2,
                col=2
            )

        # ==========================================================
        # LAYOUT
        # ==========================================================

        fig.update_layout(

            template="plotly_dark",

            title={
                "text": "Análise Comparativa de Ações",
                "x": 0.5,
                "xanchor": "center"
            },

            # Ocupa todo o espaço disponível
            autosize=True,

            # Remove margens grandes
            margin=dict(
                l=30,
                r=30,
                t=60,
                b=30
            ),

            hovermode="closest",

            # Legenda
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.01,
                xanchor="center",
                x=0.5
            )
        )

        # ==========================================================
        # EIXOS 2D
        # ==========================================================

        fig.update_xaxes(
            title_text="Data",
            row=1,
            col=1
        )

        fig.update_yaxes(
            title_text="Close",
            row=1,
            col=1
        )

        fig.update_xaxes(
            title_text="Close",
            row=1,
            col=2
        )

        fig.update_yaxes(
            title_text="Frequência",
            row=1,
            col=2
        )

        fig.update_xaxes(
            title_text="Volume",
            row=2,
            col=1
        )

        fig.update_yaxes(
            title_text="Close",
            row=2,
            col=1
        )

        # ==========================================================
        # EIXOS 3D
        # ==========================================================

        fig.update_scenes(

            xaxis_title="Open",
            yaxis_title="Close",
            zaxis_title="Volume",

            # Aproveita melhor o espaço do quadrante
            aspectmode="auto",

            row=2,
            col=2
        )
        fig.update_layout(
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.02,
                xanchor="center",
                x=0.5
            )
        )

        # ==========================================================
        # HTML
        # ==========================================================

        caminho_ht = r".\graficos\comparativo"

        os.makedirs(
            caminho_ht,
            exist_ok=True
        )

        arquivo_html = os.path.join(
            caminho_ht,
            "Comparativo.html"
        )

        # ==========================================================
        # HTML OCUPANDO 100% DA JANELA
        # ==========================================================

        fig.write_html(
            arquivo_html,
            full_html=True,
            include_plotlyjs=True,
            config={
                "responsive": True
            }
        )

        # ==========================================================
        # ABRIR NAVEGADOR
        # ==========================================================

        webbrowser.open(
            "file://" + os.path.abspath(arquivo_html)
        )
  

