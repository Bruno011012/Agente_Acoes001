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
from agente_acoes_anls import CLasse_agtacoes_analyses



class CLasse_agtacoes_ge01() :
    def __init__(self,query):
        self.query = query
        self.desencadear()


    def desencadear(self) :
        self.criar_parametros()
        self.pepiline()


    def manipulacao_empresas_datas(self,tipo=None,x=None) :
        if tipo == 0 :
            "Empresas"
            lista_va = []
            if x != None :
                if re.search("-",x) :
                    lista_emp = x.split("-")
                    return lista_emp
                else :
                    return lista_va.append(x)
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
        else :
            empresas = self.reconhecimento_empresas()
            datas_ref = self.reconhecimento_datas()
            empres_ref01 = self.manipulacao_empresas_datas(0,empresas)
            datas_ref01 = self.manipulacao_empresas_datas(1,datas_ref)
            print(f"{intencao} {empresas} {datas_ref}")
            self.pepiline_analyses(empres_ref01,datas_ref01)


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


        

CLasse_agtacoes_ge01("Me de uma analise do banco do brasil e da Ambev")