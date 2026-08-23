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


class CLasse_agtacoes_ml() :
    def __init__(self,empre_ref,qnt_mes):
        self.empre_ref = empre_ref
        self.qtd_mes = qnt_mes
        self.desencadear()


    def desencadear(self) :
        self.criar_parametros()
        self.conferencia_param_ditrei()
        self.criacao_tb_origem()
        self.funcao_invocar_base_previsao()
        self.criacao_base_treino_teste()
        self.criacao_modelo_bayes()
        self.criar_grafico_simulacao()
        

    def criar_parametros(self) :
        self.modelo_bossting = CLasse_agtacoes_ml_boost(self.empre_ref,self.qtd_mes)
        self.tabelas = CLasse_agtacoes_q()


    def conferencia_param_ditrei(self) :
        if self.qtd_mes <= 10 :
            self.val_sdiame = 10
        elif self.qtd_mes > 10 and self.qtd_mes <= 30:
            self.val_sdiame = 20
        elif self.qtd_mes > 30 and self.qtd_mes <= 70:
            self.val_sdiame = 55
        elif self.qtd_mes > 70 and self.qtd_mes <= 100:
            self.val_sdiame = 95
        else :
            self.val_sdiame = 360


    def criacao_tb_origem(self) :
        data_ref02 = datetime.now().strftime("%Y-%m-%d")
        data_ref01 = (datetime.now() - timedelta(days=(31 + self.val_sdiame))).strftime("%Y-%m-%d")
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


    def funcao_invocar_base_previsao(self) :
        frame_tr = self.modelo_bossting.desencadear()
        frame_tr["Dia"] = frame_tr["Date"].map(lambda x : x.day)
        frame_tr["Mes"] = frame_tr["Date"].map(lambda x : x.month)
        frame_tr = self.engenharia_features_signal(frame_tr)
        self.frame_ts0 = frame_tr.copy()



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
        df_train = self.frame_tr.reset_index(drop=True)
        df_test = self.frame_ts0
        self.df_test0 = df_test.copy()
        self.stander_y = StandardScaler()
        self.stander_x = StandardScaler()
        self.x_train = self.stander_x.fit_transform(df_train[features])
        self.x_test = self.stander_x.transform(df_test[features])
        self.y_train = self.stander_y.fit_transform(df_train[[target]]).flatten()
        self.y_test = self.stander_y.transform(df_test[[target]]).flatten()
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
        print("Base Previsao")
        print(frame_final1)
        colunas_ref = ["Date","Open","High","Low","Previsto","Volume","Nome_Empresa"]
        colunas_ref_1 = ["Date","Open","High","Low","Close","Volume","Empresas"]
        frame_final2 = frame_final1[colunas_ref]
        frame_final2 = frame_final2.rename(columns={"Previsto":"Close","Nome_Empresa":"Empresas"})
        frame_final2["Status"] = "Simulacao"
        frame_concat = self.frame_tr[colunas_ref_1]
        nome_eempre = frame_concat.loc[0,"Empresas"]
        frame_concat["Status"] = "Historico"
        frame_final3 = pd.concat([frame_concat,frame_final2]).reset_index(drop=True)
        caminho_dest = r".\planilhas\simulacao"
        arquivo_des = os.path.join(caminho_dest,f"Simulacao_{self.nome_empresa_glob}.json")
        frame_final3["Date"] = frame_final3["Date"].astype(str)
        frame_final3["Empresas"] = nome_eempre
        frame_final3.to_json(arquivo_des,orient="records",force_ascii=False,indent=4)
        print(frame_final3)


    def criar_grafico_simulacao(self) :
        caminho_bs = os.path.join(r".\planilhas\simulacao",f"Simulacao_{self.nome_empresa_glob}.json")
        caminho_ht = os.path.join(r".\graficos\simulacoes",f"simulacao_ml_{self.nome_empresa_glob}.html")
        frame_tr = pd.DataFrame(pd.read_json(caminho_bs))
        frame_tr["Date"] = pd.to_datetime(frame_tr["Date"],errors="coerce")
        grafico_01 = px.line(frame_tr,x="Date",y="Close",color="Status",title=f"Simulação Modelo - (Pymc Bayes) {self.qtd_mes} Dias Empresa {self.frame_tr.loc[0,'Empresas']}",markers=True,template="plotly_dark")
        grafico_01.write_html(caminho_ht,full_html=True,
                    include_plotlyjs=True,
                    config={
                        "responsive": True
                    })
        webbrowser.open(caminho_ht)



class CLasse_agtacoes_ml_boost() :
    def __init__(self,empre_ref,qtd_mes) :
        self.empre_ref = empre_ref
        self.qtd_mes = qtd_mes


    def desencadear(self) :
        self.criar_parametros()
        self.criar_tabela_origem()
        self.decodificar_base()
        colunas_ref = [x for x in list(self.frame_tr.columns) if x not in ["Date","Ticker","Nome_Empresa","Dia","Mes","Empresas"]]
        dict_resul = {}
        lista_fim = []
        date_ref = datetime.now()
        for u in range(self.qtd_mes) :
            for col_ref in colunas_ref :
                target = col_ref
                features = [x for x in colunas_ref if x not in [target]]
                self.criar_parametros_modelo(target)
                self.criar_base_treino_teste()
                self.criar_modelo_bossting()
                self.treinar_modelo()
                y_predict = self.previsao_modelo()
                dict_resul[col_ref] = y_predict
            lista_fim.append({"Date":date_ref,"Ticker":0,"Close":dict_resul["Close"],"High":dict_resul["High"],"Low":dict_resul["Low"],"Open":dict_resul["Open"],"Volume":dict_resul["Volume"],"Nome_Empresa":0,"Mes":date_ref.month,"Dia":date_ref.day})
            frame_ff01 = self.decodificar_base_nvframe(pd.DataFrame(lista_fim))
            self.frame_tr = pd.concat([self.frame_tr,frame_ff01]).reset_index(drop=True)
            date_ref = date_ref + relativedelta(days=1)
            print(u)
        frame_final = pd.DataFrame(lista_fim)
        frame_final["Date"] = pd.to_datetime(frame_final["Date"],errors="coerce")
        return frame_final




    def criar_parametros(self) :
        self.tabelas = CLasse_agtacoes_q()


    def criar_tabela_origem(self) :
        data_ref02 = datetime.now().strftime("%Y-%m-%d")
        data_ref01 = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")
        frame_tr = self.tabelas.tabela_acoes(self.empre_ref,data_ref01,data_ref02)
        frame_tr["Date"] = pd.to_datetime(frame_tr["Date"],errors="coerce")
        frame_tr["Mes"] =  frame_tr["Date"].map(lambda x : x.month)
        frame_tr["Dia"] =  frame_tr["Date"].map(lambda x : x.day)
        frame_tr = frame_tr.drop_duplicates(subset=["Date","Ticker","Close"]).reset_index(drop=True)
        frame_tr = frame_tr.sort_values(by="Date").reset_index(drop=True)
        print(frame_tr["Ticker"].value_counts())
        self.frame_tr = frame_tr.copy()



    def criar_parametros_modelo(self,alvo) :
        self.target = alvo
        self.features = [x for x in list(self.frame_tr.columns) if x not in [self.target,"Ticker","Date","Nome_Empresa","Empresas"]]


    def decodificar_base(self) :
        decolder = LabelEncoder()
        for col in list(self.frame_tr.columns) :
            if self.frame_tr[col].dtypes == "object" :
                self.frame_tr[col] = decolder.fit_transform(self.frame_tr[col])


    def decodificar_base_nvframe(self,data) :
        decolder = LabelEncoder()
        for col in list(data.columns) :
            if data[col].dtypes == "object" :
                data[col] = decolder.fit_transform(data[col])
        return data


    def criar_base_treino_teste(self) :
        df_train = self.frame_tr.iloc[:(len(self.frame_tr) - 1)].reset_index(drop=True)
        df_test = self.frame_tr.iloc[(len(self.frame_tr) - 1):].reset_index(drop=True)
        self.x_train = df_train[self.features]
        self.x_test = df_test[self.features]
        self.y_train = df_train[self.target]
        self.y_test = df_test[self.target]

    

    def criar_modelo_bossting(self) :
        self.modelo_bossting = GradientBoostingRegressor(
            n_estimators=500,          # mais árvores costumam ajudar
            learning_rate=0.05,        # menor que o default (0.1) → melhor generalização
            max_depth=4,               # 3–6 é o sweet spot
            min_samples_split=5,
            min_samples_leaf=3,
            subsample=0.8,             # stochastic gradient boosting (reduz overfitting)
            max_features='sqrt',       # ou 0.8 / 'log2'
            loss='squared_error',      # ou 'huber' se tiver outliers
            random_state=42,
            n_iter_no_change=20,       # early stopping
            validation_fraction=0.1,
            tol=1e-4)


    def treinar_modelo(self) :
        self.modelo_bossting.fit(self.x_train,self.y_train)


    def previsao_modelo(self) :
        y_predict = self.modelo_bossting.predict(self.x_test)
        return y_predict[0]

    