import pandas as pd 
import random as rd 
import numpy as np 
import os 
import shutil
import re 
from functools import partial
from toolz import compose,compose_left
from sklearn.ensemble import RandomForestRegressor,GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder,StandardScaler
from sklearn.model_selection import train_test_split
from scipy.signal import butter, sosfilt, detrend, welch
from scipy.stats import skew, kurtosis
import pymc as pm
from agente_acoes_q import CLasse_agtacoes_q
import pprint
import collections
from datetime import datetime,timedelta,date
import time
import calendar
from dateutil.relativedelta import relativedelta
import plotly.express as px 
import webbrowser
from plotly.subplots import make_subplots
import plotly.io as pio
import plotly.graph_objects as go


class CLasse_agtacoes_ml_indi() :
    def __init__(self,empre_ref,qnt_mes):
        self.empre_ref = empre_ref
        self.qtd_mes = qnt_mes
        self.desencadear()


    def desencadear(self) :
        self.criar_parametros()
        self.criar_logica_treino()
        self.criacao_tb_origem()
        self.criacao_base_treino_teste()
        self.criacao_modelo_bayes()
        self.criacao_indicadores_analyses()
    

    def criar_logica_treino(self) :
        valor_base = 40
        num_ref = (valor_base - int(self.qtd_mes))
        print(num_ref)
        self.val_treit = 0
        if num_ref <= 16 :
            self.val_treit = 50
        elif num_ref > 16 and num_ref <= 40 :
            self.val_treit = 40
        elif num_ref > 40 :
            self.val_treit = 10


    def criar_parametros(self) :
        self.tabelas = CLasse_agtacoes_q()


    def criacao_tb_origem(self) :
        data_ref02 = datetime.now().strftime("%Y-%m-%d")
        data_ref01 = (datetime.now() - timedelta(days=(40 + self.val_treit))).strftime("%Y-%m-%d")
        frame_tr = self.tabelas.tabela_acoes(self.empre_ref,data_ref01,data_ref02)
        frame_tr["Date"] = pd.to_datetime(frame_tr["Date"],errors="coerce")
        frame_tr = frame_tr.sort_values(by="Date").reset_index(drop=True)
        frame_tr = frame_tr.drop_duplicates(subset=["Date","Ticker","Close"]).reset_index(drop=True)
        frame_tr = self.engenharia_features_signal(frame_tr)
        frame_tr["Mes"] = frame_tr["Date"].map(lambda x : x.month)
        frame_tr["Dia"] = frame_tr["Date"].map(lambda x : x.day)
        print(frame_tr)
        self.nome_empresa_glob = frame_tr.loc[0,"Empresas"]
        self.frame_tr = frame_tr.copy()




    def engenharia_features_signal(self,df):
        df = df.copy()
        df = df.sort_values("Date").reset_index(drop=True)

        # ==========================================================
        # 1. FEATURES BÁSICAS — SEM CLOSE
        # ==========================================================

        df["Range"] = df["High"] - df["Low"]

        df["Range_Pct"] = (
            df["Range"] / (df["Open"] + 1e-8)
        )

        df["Open_Return"] = df["Open"].pct_change()

        df["Volume_Change"] = df["Volume"].pct_change()

        df["Open_Position"] = (
            (df["Open"] - df["Low"]) /
            (df["Range"] + 1e-8)
        )

        # ==========================================================
        # 2. LAGS
        # ==========================================================

        for lag in [1, 2, 3, 5, 10]:

            df[f"Open_Lag_{lag}"] = (
                df["Open"].shift(lag)
            )

            df[f"Volume_Lag_{lag}"] = (
                df["Volume"].shift(lag)
            )

            df[f"Range_Lag_{lag}"] = (
                df["Range"].shift(lag)
            )

        # ==========================================================
        # 3. ESTATÍSTICAS ROLLING
        # ==========================================================

        for w in [5, 10, 20]:

            # Open
            df[f"Open_Mean_{w}"] = (
                df["Open"].rolling(w).mean()
            )

            df[f"Open_Std_{w}"] = (
                df["Open"].rolling(w).std()
            )

            df[f"Open_Skew_{w}"] = (
                df["Open"]
                .rolling(w)
                .apply(
                    lambda x: skew(x, bias=False),
                    raw=True
                )
            )

            df[f"Open_Kurtosis_{w}"] = (
                df["Open"]
                .rolling(w)
                .apply(
                    lambda x: kurtosis(x, bias=False),
                    raw=True
                )
            )

            # Range
            df[f"Range_Mean_{w}"] = (
                df["Range"].rolling(w).mean()
            )

            df[f"Range_Std_{w}"] = (
                df["Range"].rolling(w).std()
            )

            # Volume
            df[f"Volume_Mean_{w}"] = (
                df["Volume"].rolling(w).mean()
            )

            df[f"Volume_Std_{w}"] = (
                df["Volume"].rolling(w).std()
            )

            # Volume relativo
            df[f"Volume_Relative_{w}"] = (
                df["Volume"] /
                (
                    df[f"Volume_Mean_{w}"] +
                    1e-8
                )
            )

            # Z-score do Open
            df[f"Open_ZScore_{w}"] = (
                (
                    df["Open"] -
                    df[f"Open_Mean_{w}"]
                ) /
                (
                    df[f"Open_Std_{w}"] +
                    1e-8
                )
            )

        # ==========================================================
        # 4. DETRENDING ROLLING
        # ==========================================================

        def detrend_last(x):

            if len(x) < 3:
                return np.nan

            return detrend(x)[-1]

        df["Open_Detrend_20"] = (
            df["Open"]
            .rolling(20)
            .apply(
                detrend_last,
                raw=True
            )
        )

        # ==========================================================
        # 5. BUTTERWORTH CAUSAL
        # ==========================================================
        #
        # NÃO usar sosfiltfilt.
        # sosfilt usa somente o fluxo passado -> presente.
        #

        def butter_lowpass(series):

            x = (
                series
                .ffill()
                .bfill()
                .values
            )

            sos = butter(
                3,
                0.10,
                btype="low",
                fs=1.0,
                output="sos"
            )

            return sosfilt(sos, x)

        df["Open_LowPass"] = (
            butter_lowpass(df["Open"])
        )

        df["Volume_LowPass"] = (
            butter_lowpass(df["Volume"])
        )

        # Desvio em relação à tendência
        df["Open_Filter_Deviation"] = (
            df["Open"] -
            df["Open_LowPass"]
        )

        # ==========================================================
        # 6. ENERGIA ESPECTRAL — WELCH
        # ==========================================================

        def spectral_energy(x):

            if len(x) < 16:
                return np.nan

            x = x - np.mean(x)

            _, power = welch(
                x,
                fs=1.0,
                nperseg=min(16, len(x))
            )

            return np.sum(power)

        df["Open_Spectral_Energy"] = (
            df["Open"]
            .rolling(20)
            .apply(
                spectral_energy,
                raw=True
            )
        )

        # ==========================================================
        # 7. EXTREMOS
        # ==========================================================

        df["Open_Max_20"] = (
            df["Open"].rolling(20).max()
        )

        df["Open_Min_20"] = (
            df["Open"].rolling(20).min()
        )

        df["Open_Position_20"] = (
            (
                df["Open"] -
                df["Open_Min_20"]
            ) /
            (
                df["Open_Max_20"] -
                df["Open_Min_20"] +
                1e-8
            )
        )

        # ==========================================================
        # 8. FEATURES TEMPORAIS
        # ==========================================================

        date = pd.to_datetime(df["Date"])

        df["DayOfWeek"] = date.dt.dayofweek
        df["Month"] = date.dt.month
        df["DayOfMonth"] = date.dt.day

        df["DayOfWeek_Sin"] = np.sin(
            2 * np.pi * df["DayOfWeek"] / 7
        )

        df["DayOfWeek_Cos"] = np.cos(
            2 * np.pi * df["DayOfWeek"] / 7
        )

        df["Month_Sin"] = np.sin(
            2 * np.pi * df["Month"] / 12
        )

        df["Month_Cos"] = np.cos(
            2 * np.pi * df["Month"] / 12
        )

        # ==========================================================
        # 9. LIMPEZA
        # ==========================================================

        df = df.replace(
            [np.inf, -np.inf],
            np.nan
        )
        df = df.fillna(0)
        return df


    def criacao_base_treino_teste(self) :
        target = "Close"
        features = [x for x in list(self.frame_tr.columns) if x not in [target,"Date","Ticker","Nome_Empresa","Empresas"]]
        df_train = self.frame_tr.iloc[:(len(self.frame_tr) - self.qtd_mes)].reset_index(drop=True)
        df_test = self.frame_tr.iloc[(len(self.frame_tr) - self.qtd_mes):].reset_index(drop=True)
        self.df_test0 = df_test.copy()
        self.stander_y = StandardScaler()
        self.stander_x = StandardScaler()
        self.x_train = self.stander_x.fit_transform(df_train[features])
        self.x_test = self.stander_x.transform(df_test[features])
        self.y_train = self.stander_y.fit_transform(df_train[[target]]).flatten()
        self.y_test = self.stander_y.transform(df_test[[target]]).flatten()
        print(df_train)
        print(df_test)
        print(f"Shape x_train{self.x_train.shape}")
        print(f"Shape x_test{self.x_test.shape}")
        print(f"Shape y_train{self.y_train.shape}")
        print(f"Shape y_test{self.y_test.shape}")
        

    def criacao_modelo_bayes(self) :
        lista_frame = []
        with pm.Model() as model :
            X_data = pm.Data("X_data",self.x_train)
            y_data = pm.Data("y_data",self.y_train)
            alpha = pm.Normal("alpha", mu=0, sigma=1)
            tau = pm.HalfNormal("tau", sigma=1)
            beta = pm.Normal("beta", mu=0, sigma=tau, shape=self.x_train.shape[1])
            sigma = pm.HalfNormal("sigma", sigma=1)
            mu = alpha + pm.math.dot(X_data,beta)
            Y_obs = pm.Normal("Y_obs",mu=mu,sigma=sigma,observed=y_data)
            idata = pm.sample(draws=150,tune=150,chains=1,cores=1)
        with model :
            pm.set_data({"X_data":self.x_test,"y_data":self.y_test})
            predicoes_01 = pm.sample_posterior_predictive(idata,var_names=["Y_obs"],predictions=True).predictions
            y_predct0 = predicoes_01["Y_obs"].mean(dim=("chain", "draw")).values
            y_previsto = self.stander_y.inverse_transform(y_predct0.reshape(-1,1)).flatten()
            y_real = self.stander_y.inverse_transform(self.y_test.reshape(-1,1)).flatten()
            for val_ref0,val_ref1 in zip(y_previsto,y_real) :
                lista_frame.append({"Previsto":val_ref0,"Real":val_ref1})
            frame_final = pd.DataFrame(lista_frame)
            frame_final1 = pd.concat([frame_final,self.df_test0],axis=1)
        colunas_ref_1 = ["Date","Open","High","Low","Previsto","Real","Volume","Empresas"]
        frame_final1 = frame_final1[colunas_ref_1]
        frame_final1["Variacao"] = frame_final1["Previsto"] - frame_final1["Real"] 
        frame_final1["Erro_Medio"] = frame_final1["Variacao"].mean()
        frame_final1["Erro_Mediana"] = frame_final1["Variacao"].median()
        frame_final1["Erro_Desvio"] = frame_final1["Variacao"].std()
        frame_final1[["Open","High","Low","Previsto","Real","Volume","Variacao","Erro_Medio","Erro_Mediana","Erro_Desvio"]] = frame_final1[["Open","High","Low","Previsto","Real","Volume","Variacao","Erro_Medio","Erro_Mediana","Erro_Desvio"]].map(lambda x : round(float(x),2))
        self.frame_analyses = frame_final1.copy()
        print(frame_final1)


    def criacao_indicadores_analyses(self) :
        grafico_01 = px.line(self.frame_analyses,x="Date",y="Variacao",markers=True,title="Variação de erro na previsão",template="plotly_dark")
        grafico_02 = px.histogram(self.frame_analyses,x=["Previsto","Real"],template="plotly_dark",title="Distribuições",barmode="overlay")
        grafico_03 = px.line(self.frame_analyses,x="Date",y=["Previsto","Real"],markers=True,title="Tendencia Simulação",template="plotly_dark")
        grafico_04 = px.scatter(self.frame_analyses,x="Previsto",y="Real",trendline="lowess",trendline_color_override="red",template="plotly_dark")
        grafico_05 = px.scatter_3d(self.frame_analyses,x="Previsto",y="Real",z="Variacao",template="plotly_dark")
        grafico_06 = px.violin(self.frame_analyses,x="Variacao",title="Distribuições Variação",template="plotly_dark")
        fig = make_subplots(
        rows=4,
        cols=2,

        # O gráfico 05 ocupa as duas colunas
        specs=[
            [{"type": "xy"}, {"type": "xy"}],
            [{"type": "xy"}, {"type": "xy"}],
            [{"type": "scene"}, {"type": "xy"}],
            [{"type": "table", "colspan": 2}, None]
        ],

        subplot_titles=[
            "Variação de erro na previsão",
            "Distribuição: Previsto vs Real",
            "Tendência da Simulação",
            "Previsto vs Real",
            "Erro da previsão em 3D",
            "Distribuição da Variação",
            "Dados da Simulação"
        ],

        vertical_spacing=0.08,
        horizontal_spacing=0.06
        )

        # 01
        for trace in grafico_01.data:
            fig.add_trace(trace, row=1, col=1)

        # 02
        for trace in grafico_02.data:
            fig.add_trace(trace, row=1, col=2)

        # 03
        for trace in grafico_03.data:
            fig.add_trace(trace, row=2, col=1)

        # 04
        for trace in grafico_04.data:
            fig.add_trace(trace, row=2, col=2)

        # 05
        for trace in grafico_05.data:
            fig.add_trace(trace, row=3, col=1)
        # 06

        for trace in grafico_06.data:
            fig.add_trace(trace, row=3, col=2)
        tabela = go.Table(

        # =========================
        # CABEÇALHO
        # =========================
        header=dict(
            values=[
                "<b>EMPRESA</b>",
                "<b>DATA</b>",
                "<b>PREVISTO</b>",
                "<b>REAL</b>",
                "<b>OPEN</b>",
                "<b>HIGH</b>",
                "<b>LOW</b>",
                "<b>VOLUME</b>",
                "<b>VARIAÇÃO</b>",
                "<b>ERRO MÉDIO</b>",
                "<b>ERRO MEDIANA</b>",
                "<b>ERRO DESVIO</b>"
            ],

            align="center",

            fill=dict(
                color="#081120"
            ),

            font=dict(
                color="#00F5FF",
                size=12,
                family="Arial"
            ),

            line=dict(
                color="#00F5FF",
                width=1
            ),

            height=35
        ),

        # =========================
        # CÉLULAS
        # =========================
        cells=dict(

            values=[
                self.frame_analyses["Empresas"],
                self.frame_analyses["Date"],
                self.frame_analyses["Previsto"].round(4),
                self.frame_analyses["Real"].round(4),
                self.frame_analyses["Open"].round(4),
                self.frame_analyses["High"].round(4),
                self.frame_analyses["Low"].round(4),
                self.frame_analyses["Volume"],
                self.frame_analyses["Variacao"].round(4),
                self.frame_analyses["Erro_Medio"].round(4),
                self.frame_analyses["Erro_Mediana"].round(4),
                self.frame_analyses["Erro_Desvio"].round(4)
            ],

            align="center",

            fill=dict(
                color=[
                    ["#0B1626", "#101D30"]
                    * (len(self.frame_analyses) // 2 + 1)
                ]
                * 12
            ),

            font=dict(
                color="#D9E1E8",
                size=11,
                family="Arial"
            ),

            line=dict(
                color="#18496F",
                width=1
            ),

            height=30
        )
        )
        fig.add_trace(
            tabela,
            row=4,
            col=1
        )
        fig.update_layout(
            template="plotly_dark",

            title=dict(
                text=f"Rendimento do Modelo - (Pymc Bayes) {self.nome_empresa_glob}",
                x=0.5,
                xanchor="center"
            ),

            height=1100,

            margin=dict(
                l=30,
                r=30,
                t=80,
                b=30
            ),

            showlegend=True
        )

        # Eixos dos gráficos 2D
        fig.update_xaxes(
            showgrid=True,
            zeroline=False,
            title_text="Data",
            row=1,
            col=1
        )

        fig.update_yaxes(
            showgrid=True,
            zeroline=False,
            title_text="Variação",
            row=1,
            col=1
        )


        fig.update_xaxes(
            showgrid=True,
            zeroline=False,
            title_text="Valor",
            row=1,
            col=2
        )


        fig.update_yaxes(
            showgrid=True,
            zeroline=False,
            title_text="Frequência",
            row=1,
            col=2
        )


        fig.update_xaxes(
            showgrid=True,
            zeroline=False,
            title_text="Data",
            row=2,
            col=1
        )

        fig.update_yaxes(
            showgrid=True,
            zeroline=False,
            title_text="Valor",
            row=2,
            col=1
        )


        fig.update_xaxes(
            showgrid=True,
            zeroline=False,
            title_text="Previsto",
            row=2,
            col=2
        )

        fig.update_yaxes(
            showgrid=True,
            zeroline=False,
            title_text="Real",
            row=2,
            col=2
        )
        fig.update_xaxes(
            title_text="Variação",
            showgrid=True,
            zeroline=False,
            row=3,
            col=2
        )

        fig.update_yaxes(
            title_text="Frequência",
            showgrid=True,
            zeroline=False,
            row=3,
            col=2
        )
        fig.update_scenes(
        xaxis_title="Previsto",
        yaxis_title="Real",
        zaxis_title="Variação",
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True),
        zaxis=dict(showgrid=True),
        row=3,
        col=1
        )

        # HTML ocupando 100% da tela
        html = fig.to_html(
            full_html=True,
            include_plotlyjs=True,
            config={
                "responsive": True,
                "displaylogo": False
            }
        )
        caminho_ref = r".\graficos\rendimento_sim"
        arquivo_slv = os.path.join(caminho_ref,f"Indicadores_simulacao_{self.nome_empresa_glob}.html")
        with open(
            arquivo_slv,
            "w",
            encoding="utf-8"
        ) as arquivo:

            arquivo.write(html)

        webbrowser.open(arquivo_slv)
