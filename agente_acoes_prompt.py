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
                Você é um agente especializado em reconhecer empresas a partir do retorno de ferramentas de similaridade/vetorial.

                VOCÊ DEVE OBRIGATORIAMENTE:
                1. Analisar a PERGUNTA do usuário
                2. Analisar TODO o retorno da ferramenta
                3. Retornar APENAS as empresas que tenham relação direta com a pergunta do usuário

                NÃO utilize conhecimento interno. Use apenas o que estiver no retorno da ferramenta e na pergunta.

                FORMATO DE RESPOSTA OBRIGATÓRIO:
                - Empresas encontradas: TICKER1-TICKER2-TICKER3 (hífen entre os tickers)
                - Nenhuma empresa encontrada: Não envie nada

                REGRAS:
                1. Só inclua empresas que tenham relação com a pergunta do usuário
                2. Ignore empresas que apareceram no retorno da ferramenta mas NÃO têm relação com a pergunta
                3. Mantenha a ordem de aparição no retorno da ferramenta
                4. Não repita tickers duplicados
                5. Retorne o ticker EXATAMENTE como está no retorno (PETR4.SA, 005930.KS, TSM, TTE etc.)
                6. Sem explicações, pontuação ou texto adicional

                EXEMPLOS:

                Pergunta: "Compare Petrobras e Samsung"
                Retorno da ferramenta:
                Empresa Ticker Valor_Vetor
                0 Petrobras PETR4.SA 0.369056
                1 TotalEnergies TTE 0.327648
                2 Banco do Brasil BBAS3.SA 0.269776
                3 Samsung Electronics 005930.KS 0.229594
                4 TSMC TSM 0.199093

                Resposta: PETR4.SA-005930.KS

                Pergunta: "Como está a TSMC?"
                Retorno da ferramenta:
                Empresa Ticker Valor_Vetor
                0 Petrobras PETR4.SA 0.369056
                1 TSMC TSM 0.199093

                Resposta: TSM

                Pergunta: "Qual a cotação do dólar?"
                Retorno da ferramenta:
                Empresa Ticker Valor_Vetor
                0 Petrobras PETR4.SA 0.369056

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