import pandas as pd 
import os 
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from functools import partial
from toolz import compose,compose_left
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from noticias.noticias.spiders.noticias_01 import Noticias01Spider
from noticias.noticias.spiders.noticias_02 import Noticias02Spider
from noticias.noticias.spiders.noticias_03 import Noticias03Spider
from noticias.noticias.spiders.noticias_04 import Noticias04Spider
from noticias.noticias.spiders.noticias_05 import Noticias05Spider
from noticias.noticias.spiders.noticias_06 import Noticias06Spider
from noticias.noticias.spiders.noticias_07 import Noticias07Spider

from scrapy import cmdline
import re 
from collections import Counter
import sqlite3
from datetime import datetime,timedelta,date



class CLasse_agtacoes_scr() :
    def __init__(self) :
        self.desencadear()


    def desencadear(self) :
        self.disparar_spider()
        self.tratamento_01()
        self.tratamento_02()
        self.tratamento_03()
        self.tratamento_04()
        self.tratamento_05()
        self.tratamento_06()
        self.tratamento_07()
        self.consolidar_final()

    def disparar_spider(self) :
        process = CrawlerProcess(
            get_project_settings()
        )

        process.crawl(Noticias01Spider)
        process.crawl(Noticias02Spider)
        process.crawl(Noticias03Spider)
        process.crawl(Noticias04Spider)
        process.crawl(Noticias05Spider)
        process.crawl(Noticias06Spider)
        process.crawl(Noticias07Spider)
        

        process.start()
    


    def tratamento_01(self) :
        data_ref_dd = datetime.now().strftime("%d/%m/%Y")
        caminho = r".\data\noticias\noticias_1.json"
        frame_tr = pd.DataFrame(pd.read_json(caminho))
        frame_tr = frame_tr.fillna("-")
        frame_tr["Quant01"] = frame_tr["noticia_01"].map(lambda x : len(x))
        frame_tr["Quant02"] = frame_tr["noticia_02"].map(lambda x : len(x))
        lista_ref = []
        for i , val_ref in enumerate(frame_tr["noticia_01"]) :
            val_ref_02 = frame_tr.loc[i,"noticia_02"]
            if val_ref.strip() != "-" and len(val_ref) > 10 :
                lista_ref.append({"Noticia":val_ref,"Data_ref":data_ref_dd,"Link":frame_tr.loc[i,"Link"]})
            if val_ref_02.strip() != "-" and len(val_ref_02) > 10 :
                lista_ref.append({"Noticia":val_ref_02,"Data_ref":data_ref_dd,"Link":frame_tr.loc[i,"Link"]})
        filtro_01 = pd.DataFrame(lista_ref)
        filtro_01 = filtro_01.drop_duplicates().reset_index(drop=True)
        filtro_01["ID_ref"] = "-"
        filtro_01["Tipo"] = "Acoes"
        caminho_ref1 = os.path.join(r".\data\noticias\diario",f"Noticiasaco_{data_ref_dd.replace('/','_')}.json") 
        filtro_01.to_json(caminho_ref1,orient="records",force_ascii=False,indent=4)
        print(filtro_01)


    def tratamento_02(self) :
        data_ref_dd = datetime.now().strftime("%d/%m/%Y")
        caminho = r".\data\noticias\noticias_2.json"
        frame_tr = pd.DataFrame(pd.read_json(caminho))
        frame_tr = frame_tr.fillna("-")
        frame_tr["Quant01"] = frame_tr["noticia_01"].map(lambda x : len(x))
        lista_ref = []
        for i , val_ref in enumerate(frame_tr["noticia_01"]) :
            if val_ref.strip() != "-" and len(val_ref) > 10 :
                lista_ref.append({"Noticia":val_ref,"Data_ref":data_ref_dd,"Link":frame_tr.loc[i,"Link"]})
        filtro_01 = pd.DataFrame(lista_ref)
        filtro_01 = filtro_01.drop_duplicates().reset_index(drop=True)
        filtro_01["ID_ref"] = "-"
        filtro_01["Tipo"] = "Geopolitica"
        caminho_ref1 = os.path.join(r".\data\noticias\diario",f"Noticiasgeo_{data_ref_dd.replace('/','_')}.json") 
        filtro_01.to_json(caminho_ref1,orient="records",force_ascii=False,indent=4)
        print(filtro_01)


    def tratamento_03(self) :
        data_ref_dd = datetime.now().strftime("%d/%m/%Y")
        caminho = r".\data\noticias\noticias_3.json"
        frame_tr = pd.DataFrame(pd.read_json(caminho))
        frame_tr = frame_tr.fillna("-")
        frame_tr["Quant01"] = frame_tr["noticia_01"].map(lambda x : len(x))
        lista_ref = []
        for i , val_ref in enumerate(frame_tr["noticia_01"]) :
            if val_ref.strip() != "-" and len(val_ref) > 10 :
                lista_ref.append({"Noticia":val_ref,"Data_ref":data_ref_dd,"Link":frame_tr.loc[i,"Link"]})
        filtro_01 = pd.DataFrame(lista_ref)
        filtro_01 = filtro_01.drop_duplicates().reset_index(drop=True)
        filtro_01["ID_ref"] = "-"
        filtro_01["Tipo"] = "Politica Nacional"
        caminho_ref1 = os.path.join(r".\data\noticias\diario",f"Noticiaspnc_{data_ref_dd.replace('/','_')}.json") 
        filtro_01.to_json(caminho_ref1,orient="records",force_ascii=False,indent=4)
        print(filtro_01)


    def tratamento_04(self) :
        data_ref_dd = datetime.now().strftime("%d/%m/%Y")
        caminho = r".\data\noticias\noticias_4.json"
        frame_tr = pd.DataFrame(pd.read_json(caminho))
        frame_tr = frame_tr.fillna("-")
        frame_tr["Quant01"] = frame_tr["noticia_01"].map(lambda x : len(x))
        lista_ref = []
        for i , val_ref in enumerate(frame_tr["noticia_01"]) :
            if val_ref.strip() != "-" and len(val_ref) > 10 :
                lista_ref.append({"Noticia":val_ref,"Data_ref":data_ref_dd,"Link":frame_tr.loc[i,"Link"]})
        filtro_01 = pd.DataFrame(lista_ref)
        filtro_01 = filtro_01.drop_duplicates().reset_index(drop=True)
        filtro_01["ID_ref"] = "-"
        filtro_01["Tipo"] = "Bolsa Americana"
        caminho_ref1 = os.path.join(r".\data\noticias\diario",f"Noticiasbeua_{data_ref_dd.replace('/','_')}.json") 
        filtro_01.to_json(caminho_ref1,orient="records",force_ascii=False,indent=4)
        print(filtro_01)

    def tratamento_05(self) :
        data_ref_dd = datetime.now().strftime("%d/%m/%Y")
        caminho = r".\data\noticias\noticias_5.json"
        frame_tr = pd.DataFrame(pd.read_json(caminho))
        frame_tr = frame_tr.fillna("-")
        frame_tr["Quant01"] = frame_tr["noticia_01"].map(lambda x : len(x))
        lista_ref = []
        for i , val_ref in enumerate(frame_tr["noticia_01"]) :
            if val_ref.strip() != "-" and len(val_ref) > 10 :
                lista_ref.append({"Noticia":val_ref,"Data_ref":data_ref_dd,"Link":frame_tr.loc[i,"Link"]})
        filtro_01 = pd.DataFrame(lista_ref)
        filtro_01 = filtro_01.drop_duplicates().reset_index(drop=True)
        filtro_01["ID_ref"] = "-"
        filtro_01["Tipo"] = "Bolsa Americana"
        caminho_ref1 = os.path.join(r".\data\noticias\diario",f"Noticiasbeua2_{data_ref_dd.replace('/','_')}.json") 
        filtro_01.to_json(caminho_ref1,orient="records",force_ascii=False,indent=4)
        print(filtro_01)


    def tratamento_06(self) :
        data_ref_dd = datetime.now().strftime("%d/%m/%Y")
        caminho = r".\data\noticias\noticias_6.json"
        frame_tr = pd.DataFrame(pd.read_json(caminho))
        frame_tr = frame_tr.fillna("-")
        frame_tr["Quant01"] = frame_tr["noticia_01"].map(lambda x : len(x))
        lista_ref = []
        for i , val_ref in enumerate(frame_tr["noticia_01"]) :
            if val_ref.strip() != "-" and len(val_ref) > 10 :
                lista_ref.append({"Noticia":val_ref,"Data_ref":data_ref_dd,"Link":frame_tr.loc[i,"Link"]})
        filtro_01 = pd.DataFrame(lista_ref)
        filtro_01 = filtro_01.drop_duplicates().reset_index(drop=True)
        filtro_01["ID_ref"] = "-"
        filtro_01["Tipo"] = "Bolsa Americana"
        caminho_ref1 = os.path.join(r".\data\noticias\diario",f"Noticiasbeua3_{data_ref_dd.replace('/','_')}.json") 
        filtro_01.to_json(caminho_ref1,orient="records",force_ascii=False,indent=4)
        print(filtro_01)

    def tratamento_07(self) :
        data_ref_dd = datetime.now().strftime("%d/%m/%Y")
        caminho = r".\data\noticias\noticias_7.json"
        frame_tr = pd.DataFrame(pd.read_json(caminho))
        frame_tr = frame_tr.fillna("-")
        frame_tr["Quant01"] = frame_tr["noticia_01"].map(lambda x : len(x))
        lista_ref = []
        for i , val_ref in enumerate(frame_tr["noticia_01"]) :
            if val_ref.strip() != "-" and len(val_ref) > 10 :
                lista_ref.append({"Noticia":val_ref,"Data_ref":data_ref_dd,"Link":frame_tr.loc[i,"Link"]})
        filtro_01 = pd.DataFrame(lista_ref)
        filtro_01 = filtro_01.drop_duplicates().reset_index(drop=True)
        filtro_01["ID_ref"] = "-"
        filtro_01["Tipo"] = "Bolsa Americana"
        caminho_ref1 = os.path.join(r".\data\noticias\diario",f"Noticiasbeua4_{data_ref_dd.replace('/','_')}.json") 
        filtro_01.to_json(caminho_ref1,orient="records",force_ascii=False,indent=4)
        print(filtro_01)


    def consolidar_final(self) :
        frame_conca = pd.DataFrame(columns=['Noticia', 'Data_ref', 'ID_ref', 'Tipo'])
        caminho_dest = os.path.join(r".\data\noticias\consolidado","Base_consolidada.parquet")
        caminho_dir = r".\data\noticias\diario"
        lista_arq = os.listdir(caminho_dir)
        for i , arq_gref in enumerate(lista_arq) :
            caminho_abr = os.path.join(caminho_dir,arq_gref)
            frame_js = pd.DataFrame(pd.read_json(caminho_abr))
            frame_conca = pd.concat([frame_conca,frame_js]).reset_index(drop=True)
        x = 1
        for i , noti_ref in enumerate(frame_conca["ID_ref"]) :
            frame_conca.loc[i,"ID_ref"] = x
            x += 1
        frame_conca = frame_conca.drop_duplicates(subset="Noticia").reset_index(drop=True)
        frame_conca.to_parquet(caminho_dest,engine="pyarrow",index=False)
        print(frame_conca)



CLasse_agtacoes_scr()