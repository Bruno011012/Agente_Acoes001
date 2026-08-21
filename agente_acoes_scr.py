import pandas as pd 
import os 
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from functools import partial
from toolz import compose,compose_left
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from noticias.noticias.spiders.noticias_01 import Noticias01Spider
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


    def disparar_spider(self) :
        process = CrawlerProcess(
            get_project_settings()
        )

        process.crawl(
            Noticias01Spider
        )

        process.start()
    


    def tratamento_01(self) :
        data_ref_dd = datetime.now().strftime("%d/%m/%Y")
        caminho = r".\bases_dados\noticias\noticias_1.json"
        frame_tr = pd.DataFrame(pd.read_json(caminho))
        frame_tr = frame_tr.fillna("-")
        frame_tr["Quant01"] = frame_tr["noticia_01"].map(lambda x : len(x))
        frame_tr["Quant02"] = frame_tr["noticia_02"].map(lambda x : len(x))
        lista_ref = []
        for i , val_ref in enumerate(frame_tr["noticia_01"]) :
            val_ref_02 = frame_tr.loc[i,"noticia_02"]
            if val_ref.strip() != "-" and len(val_ref) > 10 :
                lista_ref.append({"Noticia":val_ref,"Data_ref":data_ref_dd})
            if val_ref_02.strip() != "-" and len(val_ref_02) > 10 :
                lista_ref.append({"Noticia":val_ref_02,"Data_ref":data_ref_dd})
        filtro_01 = pd.DataFrame(lista_ref)
        filtro_01 = filtro_01.drop_duplicates().reset_index(drop=True)
        filtro_01["ID_ref"] = "-"
        x = 1
        for i , val_ref in enumerate(filtro_01["ID_ref"]) :
            filtro_01.loc[i,"ID_ref"] = x
            x += 1
        caminho_ref1 = os.path.join(r".\bases_dados\noticias\diario",f"Noticias_{data_ref_dd.replace('/','_')}.json") 
        filtro_01.to_json(caminho_ref1,orient="records",force_ascii=False,indent=4)
        print(filtro_01)




CLasse_agtacoes_scr()