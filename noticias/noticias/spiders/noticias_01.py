import scrapy


class Noticias01Spider(scrapy.Spider):
    name = "noticias_01"
    custom_settings = {
    "FEEDS": {
        r"C:\Users\beliasf\Desktop\Projetos\Agente_Acoes_V0\data\noticias\noticias_1.json": {
            "format": "json",
            "encoding": "utf-8",
            "indent": 4,
            "overwrite": True
            }
        }
        }
    allowed_domains = ["investidor10.com"]
    start_urls = ["https://investidor10.com.br/noticias/"]


    def start_requests(self):

        for url in self.start_urls:

            yield scrapy.Request(
                url=url,
                meta={
                    "playwright": True
                }
            )


    def parse(self, response):
        linha = response.css("div")
        lista_ref = []
        for linha_ref in linha :
            titulo = linha_ref.css("h3::text").get()
            titulo_01 = linha_ref.css("span::text").get()
            yield {
                "noticia_01":titulo,
                "noticia_02":titulo_01,
                "Tipo":"Acoes"

                }
            lista_ref.append(titulo)
