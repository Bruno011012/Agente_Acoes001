import spacy
import pandas as pd 
import random as rd 
import numpy as np 
import os 
import shutil
import re 
from functools import partial
from toolz import compose,compose_left
import collections
import unicodedata
import pprint



class CLasse_agtacoes_nlp() :
    def __init__(self,query):
        self.query = query
        self.criar_parametros()
        self.desencadear()
        self.desencadear_01()


    def desencadear(self) :
        self.carregar_frame_ori()
        self.criacao_chunking()
        self.busca_semantica()
        self.busca_lexica()


    def desencadear_01(self) :
        self.busca_empresa()


    def normalizar_texto(self,texto):
        if not isinstance(texto, str):
            texto = str(texto)
        
        # 1. Normaliza caracteres Unicode (ex: é -> e + ́)
        texto = unicodedata.normalize('NFKD', texto)
        
        # 2. Remove acentos (mantém apenas caracteres ASCII)
        texto = texto.encode('ASCII', 'ignore').decode('ASCII')
        
        # 3. Converte para minúsculas
        texto = texto.lower()
        
        # 4. Remove caracteres especiais (mantém letras, números e espaços)
        texto = re.sub(r'[^a-z0-9\s]', '', texto)
        
        # 5. Remove espaços extras
        texto = re.sub(r'\s+', ' ', texto).strip()
        
        return texto
    

    def criar_parametros(self) :
        self.nlp = spacy.load("pt_core_news_sm")


    def carregar_frame_ori(self) :
        caminho = r".\bases_dados\noticias\diario\Noticias_21_08_2026.json"
        frame_tr = pd.DataFrame(pd.read_json(caminho))
        self.frame_tr = frame_tr.copy()


    def criacao_chunking(self) :
        lista_chunkings = []
        for i , noticia_ref in enumerate(self.frame_tr["Noticia"]) :
            lista_chunkings.append({"ID":self.frame_tr.loc[i,"ID_ref"],"Texto":self.normalizar_texto(noticia_ref)})
        self.frame_chunk = pd.DataFrame(lista_chunkings)
        print(self.frame_chunk)


    def busca_semantica(self) :
        doc = self.nlp(self.normalizar_texto(self.query))
        lista_score = []
        for i , noti_ref in enumerate(self.frame_chunk["Texto"]) :
            doc_text = self.nlp(noti_ref)
            sm = []
            for doc_ref in doc_text :
                vector_ref = doc.similarity(doc_ref)
                sm.append(vector_ref)
            if sm :
                val_max = max(sm)
                lista_score.append({"ID":self.frame_chunk.loc[i,"ID"],"Valor":val_max})
        frame_score = pd.DataFrame(lista_score)
        frame_score = frame_score.sort_values(by="Valor",ascending=False).reset_index(drop=True).head(10)
        frame_score_01 = pd.merge(frame_score,self.frame_chunk,left_on="ID",right_on="ID",how="left",suffixes=("_x","_y"))
        self.frame_scores = frame_score_01.copy()
        print(frame_score)


    def busca_lexica(self) :
        lista_score = []
        lemma_query = {x.lemma_ for x in self.nlp(self.normalizar_texto(self.query))}
        for i , texto_ref in enumerate(self.frame_scores["Texto"]) :
            lemma_noti = {x.lemma_ for x in self.nlp(texto_ref)}
            if lemma_noti.intersection(lemma_query) :
                val_text = f""""""
                for v_r in lemma_noti.intersection(lemma_query) :
                    val_text = f"""{val_text} {v_r}"""
                lista_score.append({"ID":self.frame_scores.loc[i,"ID"],"Intensidade":len(lemma_noti.intersection(lemma_query)),"Retorno":val_text})
        frame_final = pd.DataFrame(lista_score)
        frame_final_01 = pd.merge(frame_final,self.frame_scores,left_on="ID",right_on="ID",how="left",suffixes=("_x","_y"))
        frame_final_01 = frame_final_01.sort_values(by="Intensidade",ascending=False).reset_index(drop=True).head(4)
        print(frame_final_01)


    def busca_empresa(self) :
        caminho_js = r".\documentos\empresas\empresas.json"
        frame_js = pd.DataFrame(pd.read_json(caminho_js))
        doc_q = self.nlp(self.normalizar_texto(self.query))
        lista_score = []
        for i , empre_ref in enumerate(frame_js["Nome_Empresa"]) :
            sm = []
            doc_js = self.nlp(self.normalizar_texto(empre_ref))
            for doc_ref in doc_js :
                vector_ref = doc_q.similarity(doc_ref)
                sm.append(vector_ref)
            if sm :
                val_max = max(sm)
                lista_score.append({"Empresa":empre_ref,"Ticker":frame_js.loc[i,"Ticker"],"Valor_Vetor":val_max})
        frame_res = pd.DataFrame(lista_score)
        frame_res = frame_res.sort_values(by="Valor_Vetor",ascending=False).reset_index(drop=True).head(5)
        pprint.pprint(frame_res)


CLasse_agtacoes_nlp("Gosatria de saber sobre noticias de trump e lula e sobre o banco do brasil")