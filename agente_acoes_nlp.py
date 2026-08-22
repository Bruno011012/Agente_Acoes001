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
    def __init__(self):
        self.criar_parametros()
        

    def desencadear(self,query=None) :
        self.query = query
        self.carregar_frame_ori()
        self.criacao_chunking()
        self.busca_semantica()
        noticias = self.busca_lexica()
        return noticias


    def desencadear_01(self,query=None) :
        self.query = query
        empresas = self.busca_empresa()
        return empresas


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
        caminho = r".\data\noticias\consolidado\Base_consolidada.parquet"
        frame_tr = pd.DataFrame(pd.read_parquet(caminho))
        self.frame_tr = frame_tr.copy()


    def criacao_chunking(self) :
        lista_chunkings = []
        for i , noticia_ref in enumerate(self.frame_tr["Noticia"]) :
            lista_chunkings.append({"ID":self.frame_tr.loc[i,"ID_ref"],"Texto":self.normalizar_texto(noticia_ref)})
        self.frame_chunk = pd.DataFrame(lista_chunkings)
    


    def busca_semantica(self) :
        doc = self.nlp(self.normalizar_texto(self.query))
        palavras_tempo = {"ano", "anos", "mês", "meses", "dia", "dias", "semana", "semanas"}
        lista_score = []
        for i , noti_ref in enumerate(self.frame_chunk["Texto"]) :
            doc_text = self.nlp(noti_ref)
            sm = []
            for doc_ref in doc_text :
                vector_ref = [x.similarity(doc_ref) for x in doc if not x.is_stop and not x.is_punct and not x.is_space and not x.like_num and x.text.lower() not in palavras_tempo]
                v_max = max(vector_ref)
                sm.append(v_max)
            if sm :
                val_max = max(sm)
                lista_score.append({"ID":self.frame_chunk.loc[i,"ID"],"Valor":val_max})
        frame_score = pd.DataFrame(lista_score)
        frame_score = frame_score.sort_values(by="Valor",ascending=False).reset_index(drop=True).head(10)
        frame_score_01 = pd.merge(frame_score,self.frame_chunk,left_on="ID",right_on="ID",how="left",suffixes=("_x","_y"))
        self.frame_scores = frame_score_01.copy()
        pprint.pprint(self.frame_scores)
        print([x for x in doc if not x.is_stop and not x.is_punct and not x.is_space])


    def busca_lexica(self) :
        lista_score = []
        palavras_tempo = {"ano", "anos", "mês", "meses", "dia", "dias", "semana", "semanas"}
        lemma_query = {x.lemma_ for x in self.nlp(self.normalizar_texto(self.query)) if not x.is_stop and not x.is_punct and not x.is_space and not x.like_num and x.text.lower() not in palavras_tempo}
        for i , texto_ref in enumerate(self.frame_scores["Texto"]) :
            lemma_noti = {x.lemma_ for x in self.nlp(texto_ref)}
            if lemma_noti.intersection(lemma_query) :
                val_text = f""""""
                for v_r in lemma_noti.intersection(lemma_query) :
                    val_text = f"""{val_text} {v_r}"""
                lista_score.append({"ID":self.frame_scores.loc[i,"ID"],"Intensidade":len(lemma_noti.intersection(lemma_query)),"Retorno":val_text})
        frame_final = pd.DataFrame(lista_score)
        frame_final_01 = pd.merge(frame_final,self.frame_tr,left_on="ID",right_on="ID_ref",how="left",suffixes=("_x","_y"))
        frame_final_01 = frame_final_01.sort_values(by="Intensidade",ascending=False).reset_index(drop=True).head(6)
        js_ret = frame_final_01.to_json(orient="records",force_ascii=False,indent=4)
        pprint.pprint(js_ret)
        return js_ret


    def busca_empresa(self) :
        caminho_js = r".\documentos\empresas\empresas.json"
        frame_js = pd.DataFrame(pd.read_json(caminho_js))
        doc_q = self.nlp(self.normalizar_texto(self.query))
        palavras_tempo = {"ano", "anos", "mês", "meses", "dia", "dias", "semana", "semanas"}
        lista_score = []
        for i , empre_ref in enumerate(frame_js["Nome_Empresa"]) :
            sm = []
            doc_js = self.nlp(self.normalizar_texto(empre_ref))
            for doc_ref in doc_js :
                vector_ref = [x.similarity(doc_ref) for x in doc_q if not x.is_stop and not x.is_punct and not x.is_space and not x.like_num and x.text.lower() not in palavras_tempo]
                v_max = max(vector_ref)
                sm.append(v_max)
            if sm :
                val_max = max(sm)
                lista_score.append({"Empresa":empre_ref,"Ticker":frame_js.loc[i,"Ticker"],"Valor_Vetor":val_max})
        frame_res = pd.DataFrame(lista_score)
        frame_res = frame_res.sort_values(by="Valor_Vetor",ascending=False).reset_index(drop=True).head(7)
        resposta_js =  frame_res.to_json(orient="records",force_ascii=False,indent=4)
        pprint.pprint(frame_res)
        return resposta_js
        


# nlp = CLasse_agtacoes_nlp()
# nlp.desencadear("Me de uma analise da Trump no ano de 2026 ?")