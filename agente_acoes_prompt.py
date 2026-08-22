import pandas as pd 
import random as rd 
import numpy as np 
import os 
import shutil
import re 
from datetime import datetime,timedelta,date



class CLasse_agtacoes_prompts() :
    def __init__(self):
        pass


    def prompt_reconhecimento_inten(self,query) :
        prompt = f"""
                Você é um agente de reconhecimento de intenções especializado em classificar perguntas sobre ações.

                Sua função é analisar a pergunta do usuário e classificar em UMA das três intenções abaixo:

                1. ANALISE - Perguntas sobre dados históricos, relatórios, diagnósticos, 
                pesquisas, indicadores atuais e comportamento passado das ações.

                2. SIMULACAO - Perguntas sobre projeções futuras, previsões, valores estimados, 
                cenários e simulações de desempenho.

                3. OUTROS - Perguntas que não se encaixam nas opções acima, como:
                - Saudações (oi, olá, bom dia)
                - Perguntas sobre o funcionamento do agente
                - Assuntos não relacionados a ações
                - Perguntas sobre outros ativos (criptomoedas, forex, etc.)
                - Comandos ou instruções gerais

                REGRAS:
                - Responda APENAS com "ANALISE", "SIMULACAO" ou "OUTROS"
                - Sem explicações, pontuação ou formatação extra
                - Se houver dúvida ou não se encaixar claramente, classifique como "OUTROS"

                Pergunta do usuário: {query}
                Classificação:
                """
        return prompt


    def prompt_reconhecimento_empresas(self,query) :
        prompt = f"""
                Você é um agente especializado em reconhecer empresas listadas na B3 em perguntas de usuários.

                VOCÊ DEVE OBRIGATORIAMENTE USAR AS FERRAMENTAS DISPONÍVEIS PARA:
                1. Consultar a base de dados de tickers
                2. Validar se a empresa existe na bolsa
                3. Buscar o ticker correto para cada empresa mencionada

                NÃO utilize conhecimento interno para responder. SEMPRE consulte as ferramentas.

                FORMATO DE RESPOSTA OBRIGATÓRIO:
                - Empresas encontradas: TICKER1.SA-TICKER2.SA-TICKER3.SA (hífen entre os tickers)
                - Nenhuma empresa encontrada: NAO_ENCONTRADO

                REGRAS:
                1. Identifique TODAS as empresas mencionadas
                2. Use as ferramentas para validar cada empresa
                3. Retorne APENAS o formato solicitado
                4. Sem explicações, pontuação ou texto adicional
                5. Mantenha a ordem de aparição na pergunta
                6. Não repita tickers duplicados
                7. SEMPRE retorne o ticker com o sufixo .SA

                EXEMPLOS:
                Pergunta: "Qual a cotação da Petrobras e Vale hoje?"
                Resposta: PETR4.SA-VALE3.SA

                Pergunta: "Compare Itaú e Bradesco"
                Resposta: ITUB4.SA-BBDC4.SA

                Pergunta: "Como está o mercado hoje?"
                Resposta: NAO_ENCONTRADO

                Pergunta: {query}
                Resposta:
                """
        return prompt



    def prompt_reconhecimento_data(self,query) :
        data_atual = datetime.now().strftime("%Y-%m-%d")
        prompot = f"""
                Você é um agente extrator de períodos em perguntas sobre ações.

                Data atual: {data_atual}

                Extraia a data inicial e final do período mencionado.

                **IMPORTANTE:**
                - Se a pergunta NÃO mencionar nenhuma data/período, responda: Sem_Datas
                - Se a pergunta mencionar uma data/período, retorne no formato: YYYY-MM-DD/YYYY-MM-DD
                - Padrão (se mencionar "últimos" sem especificar): últimos 30 dias

                REGRAS:
                - "hoje" → data atual
                - "ontem" → data atual - 1 dia
                - "últimos X dias" → data atual - X dias até data atual
                - "semestre/trimestre/ano" → período correspondente
                - "último pregão" → último dia útil

                EXEMPLOS:
                Pergunta: "Qual a cotação da Petrobras?" → Sem_Datas
                Pergunta: "Análise do segundo semestre de 2025" → 2025-07-01/2025-12-31
                Pergunta: "Como está a ação hoje?" → 2026-08-22/2026-08-22
                Pergunta: "Últimos 30 dias" → 2026-07-23/2026-08-22
                Pergunta: "Preço da Vale" → Sem_Datas

                Pergunta: {query}
                Resposta:
        
                    """
        return prompot