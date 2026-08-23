import pandas as pd 
import random as rd 
import numpy as np 
import os 
import shutil
import re 
from functools import partial
from toolz import compose,compose_left
import collections
from agente_acoes_agts import CLasse_agtacoes_agts
from agente_acoes_anls import CLasse_agtacoes_analyses,CLasse_agtacoes_analysesc
from agente_acoes_ml import CLasse_agtacoes_ml
from concurrent.futures import ThreadPoolExecutor
from agente_acoes_ml_ind import CLasse_agtacoes_ml_indi

class CLasse_agtacoes_ge01() :
    def __init__(self,query):
        self.query = query


    def desencadear(self) :
        self.limpeza_diretorios()
        self.criar_parametros()
        noticias = self.pepiline()
        return noticias

    

    def limpeza_diretorios(self) :
        lista_ref = [r".\graficos\analises_scipy",r".\graficos\comparativo",r".\enviar",r".\zips",r".\graficos\simulacoes",r".\planilhas\simulacao",r".\graficos\rendimento_sim"]
        for i , dir_ref in enumerate(lista_ref) :
            lista_arq = os.listdir(dir_ref)
            if len(lista_arq) >= 1 :
                for u in lista_arq :
                    arq_ex = os.path.join(dir_ref,u)
                    os.remove(arq_ex)


    def manipulacao_empresas_datas(self,tipo=None,x=None) :
        if tipo == 0 :
            "Empresas"
            lista_va = []
            if x != None :
                if re.search("-",x) :
                    lista_emp = x.split("-")
                    return lista_emp
                else :
                    lista_va.append(x)
                    return lista_va
        else :
            if x == 'Sem_Datas' :
                return 'Sem_Datas'
            else :
                lista_ref = x.split("/")
                return lista_ref
            

    def pepiline(self) :
        intencao = self.reconhecimento_intencao()
        if intencao == "OUTROS" :
            print("Outros")
            return "Outros"
        elif intencao == "ANALISE" :
            empresas = self.reconhecimento_empresas()
            datas_ref = self.reconhecimento_datas()
            empres_ref01 = self.manipulacao_empresas_datas(0,empresas)
            datas_ref01 = self.manipulacao_empresas_datas(1,datas_ref)
            print(f"{intencao} {empresas} {datas_ref}")
            noticias = self.pepiline_analyses(empres_ref01,datas_ref01)
            return noticias
        elif intencao == "SIMULACAO" :
            empresas = self.reconhecimento_empresas()
            datas_ref = self.reconhecimento_datas()
            empres_ref01 = self.manipulacao_empresas_datas(0,empresas)
            datas_ref01 = self.manipulacao_empresas_datas(1,datas_ref)
            print(f"{intencao} {empresas} {datas_ref}")
            noticias = self.pepyline_simulacao(empres_ref01)
            return noticias

    def criar_parametros(self) :
        self.agentes = CLasse_agtacoes_agts()


    def reconhecimento_intencao(self)  :
        intencao = self.agentes.agente_intencoes(self.query)
        return intencao


    def reconhecimento_empresas(self) :
        empresas = self.agentes.agente_empresas(self.query)
        return empresas


    def reconhecimento_datas(self) :
        datas = self.agentes.agente_datas(self.query)
        return datas


    def pepiline_analyses(self,empresas,datas_ref) :
        sm = []
        print(empresas)
        if len(empresas) <= 1 :
            if datas_ref == "Sem_Datas" :
                CLasse_agtacoes_analyses(empr_ref=empresas)
            else :
                CLasse_agtacoes_analyses(empr_ref=empresas,data_ref0=datas_ref[0],data_ref1=datas_ref[1])
            Classe_copiadora_zip(0)
        else :
            for a_i in empresas :
                print(a_i)
                if datas_ref == "Sem_Datas" :
                    sm.append(a_i)
                    CLasse_agtacoes_analyses(empr_ref=sm)
                else :
                    sm.append(a_i)
                    CLasse_agtacoes_analyses(empr_ref=sm,data_ref0=datas_ref[0],data_ref1=datas_ref[1])
                sm = []
            Classe_copiadora_zip(0)
            if datas_ref == "Sem_Datas" :
                CLasse_agtacoes_analysesc(empresas)
                Classe_copiadora_zip(1)
            else :
                CLasse_agtacoes_analysesc(empresas,data_ref0=datas_ref[0],data_ref1=datas_ref[1])
                Classe_copiadora_zip(1)
        noticias = self.agentes.agente_noticias_01(self.query)
        return noticias

    
    def executar_modelo(self,empresas,n_dias):
        sm = []
        for u_i in empresas:
            sm.append(u_i)
            CLasse_agtacoes_ml(sm, int(n_dias))
            sm = []


    def executar_indicadores(self,empresas,n_dias):
        sm = []
        for u_i in empresas:
            sm.append(u_i)
            CLasse_agtacoes_ml_indi(sm, int(n_dias))
            sm = []


    def pepyline_simulacao(self,empresas) :
        n_dias = self.agentes.agente_identi_dias(self.query)
        with ThreadPoolExecutor(max_workers=2) as executor:
            futuro_ml = executor.submit(
                self.executar_modelo,
                empresas,n_dias
            )

            futuro_indicadores = executor.submit(
                self.executar_indicadores,
                empresas,n_dias
            )

            # Espera as duas terminarem
            futuro_ml.result()
            futuro_indicadores.result()
        Classe_copiadora_zip(2)
        noticias = self.agentes.agente_noticias_02(self.query)
        return noticias



class Classe_copiadora_zip() :
    def __init__(self,tipo):
        self.tipo = tipo
        self.desencadear()


    def desencadear(self) :
        if self.tipo == 0 :
            self.copiar_individual()
        elif self.tipo == 1 :
            self.copiar_individual()
            self.copiar_compe()
        elif self.tipo == 2 :
            self.copiar_simu()
        self.zipar_final()


    def copiar_individual(self) :
        destino_ref = r".\enviar"
        origim_ref = r".\graficos\analises_scipy"
        shutil.copytree(origim_ref,destino_ref,dirs_exist_ok=True)


    def copiar_compe(self) :
        destino_ref = r".\enviar"
        origim_ref = r".\graficos\comparativo"
        shutil.copytree(origim_ref,destino_ref,dirs_exist_ok=True)


    def copiar_simu(self) :
        destino_ref = r".\enviar"
        origim_ref = [r".\planilhas\simulacao",r".\graficos\simulacoes",r".\graficos\rendimento_sim"]
        for i in origim_ref :
            shutil.copytree(i,destino_ref,dirs_exist_ok=True)


    def zipar_final(self) :
        origem = r".\enviar"
        destino = r".\zips"
        zip_criado = shutil.make_archive(
            base_name="analises_acoes",
            format="zip",
            root_dir=os.path.dirname(origem) or ".",
            base_dir=os.path.basename(origem)
        )

        # Move para a pasta destino
        shutil.move(zip_criado, os.path.join(destino, "analises_ml.zip"))
                


