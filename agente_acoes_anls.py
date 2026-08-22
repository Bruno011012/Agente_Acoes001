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
        self.data_ref02 = data_ref0
        self.desencadear()


    def desencadear(self) :
        self.criar_parametros()
        self.conferencia_datas_ini()
        self.carregar_tabela_ori()
        # self.grafico_01()
        # self.grafico_02()
        # self.grafico_03()
        # self.grafico_04()
        # self.grafico_05()
        # self.grafico_06()
        self.criar_subplot_final()


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
        


    def grafico_01(self) :
        caminho_grf = r".\graficos\analises_scipy"
        df = self.frame_tr
        df["suavizada"] = savgol_filter(
            df["Close"],
            window_length=21,
            polyorder=3
        )

        fig = px.line(
            df,
            x="Date",
            y=["Close", "suavizada"],
            template="plotly_dark",
            title="Série original vs. tendência suavizada"
        )
        arquivo_grf = os.path.join(caminho_grf,"tendencia_suav.html")
        fig.write_html(arquivo_grf)
        webbrowser.open(arquivo_grf)


    def grafico_02(self) :
        caminho_grf = r".\graficos\analises_scipy"
        df = self.frame_tr
        picos, _ = find_peaks(
            df["Close"],
            prominence=10
        )

        df_picos = df.iloc[picos]

        fig = px.line(
            df,
            x="Date",
            y="Close",
            template="plotly_dark",
            title="Detecção de picos"
        )

        fig.add_scatter(
            x=df_picos["Date"],
            y=df_picos["Close"],
            mode="markers",
            name="Picos"
        )
        arquivo_grf = os.path.join(caminho_grf,"deteccao_picos.html")
        fig.write_html(arquivo_grf)
        webbrowser.open(arquivo_grf)


    def grafico_03(self) :
        caminho_grf = r".\graficos\analises_scipy"
        df = self.frame_tr 
        y = df["Close"].values
        y = y - np.mean(y)

        acf = correlate(y, y, mode="full")
        acf = acf[len(y)-1:]
        acf = acf / acf[0]

        lags = np.arange(len(acf))

        df_acf = {
            "lag": lags,
            "autocorrelacao": acf
        }

        fig = px.line(
            df_acf,
            x="lag",
            y="autocorrelacao",
            template="plotly_dark",
            title="Autocorrelação da série"
        )
        arquivo_grf = os.path.join(caminho_grf,"autocorrelacao.html")
        fig.write_html(arquivo_grf)
        webbrowser.open(arquivo_grf)


    def grafico_04(self) :
        caminho_grf = r".\graficos\analises_scipy"
        df = self.frame_tr
        frequencia, potencia = periodogram(df["Close"])

        df_freq = {
            "frequencia": frequencia,
            "potencia": potencia
        }

        fig = px.line(
            df_freq,
            x="frequencia",
            y="potencia",
            template="plotly_dark",
            title="Espectro de frequência"
        )
        arquivo_grf = os.path.join(caminho_grf,"espectro.html")
        fig.write_html(arquivo_grf)
        webbrowser.open(arquivo_grf)


    def grafico_05(self) :
        caminho_grf = r".\graficos\analises_scipy"
        df = self.frame_tr
        b, a = butter(
            N=3,
            Wn=0.1,
            btype="low"
        )

        df["filtrada"] = filtfilt(
            b,
            a,
            df["Close"]
        )

        fig = px.line(
            df,
            x="Date",
            y=["Close", "filtrada"],
            template="plotly_dark",
            title="Filtro passa-baixa"
        )

        arquivo_grf = os.path.join(caminho_grf,"filtro_passab.html")
        fig.write_html(arquivo_grf)
        webbrowser.open(arquivo_grf)


    def grafico_06(self) :
        caminho_grf = r".\graficos\analises_scipy"
        df = self.frame_tr
        df["tendencia"] = savgol_filter(
        df["Close"],
            21,
            3
        )

        df["residuo"] = (
            df["Close"] - df["tendencia"]
        )

        anomalias, _ = find_peaks(
            np.abs(df["residuo"]),
            prominence=10
        )

        df["anomalia"] = False
        df.loc[df.index[anomalias], "anomalia"] = True

        fig = px.line(
            df,
            x="Date",
            y="Close",
            template="plotly_dark",
            title="Detecção de anomalias"
        )

        df_anom = df[df["anomalia"]]

        fig.add_scatter(
            x=df_anom["Date"],
            y=df_anom["Close"],
            mode="markers",
            name="Anomalias"
        )
        arquivo_grf = os.path.join(caminho_grf,"anomalias.html")
        fig.write_html(arquivo_grf)
        webbrowser.open(arquivo_grf)



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
            title=f"Análises Series Temporais - Série Temporal {self.empre_ref}"
        )

        arquivo_grf = os.path.join(caminho_grf,"consolidado.html")
        fig.write_html(arquivo_grf)
        webbrowser.open(arquivo_grf)

  

