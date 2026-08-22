from langchain.agents import create_agent
from agente_acoes_prompt import CLasse_agtacoes_prompts
from agente_acoes_tools import CLasse_agtacoes_tools
from agente_acoes_llm import CLasse_agtacoes_llm

class CLasse_agtacoes_agts(CLasse_agtacoes_llm) :
    def __init__(self):
        super().__init__()
        self.desencadear_agt01()


    def desencadear_agt01(self) :
        self.criar_parametros()


    def criar_parametros(self) :
        self.tools = CLasse_agtacoes_tools()
        self.prompts = CLasse_agtacoes_prompts()

    def verificar_resposta(self,resposta) :
        if "output" in resposta:
            print(resposta["output"])
            return resposta["output"]
        elif "messages" in resposta:
            print(resposta["messages"][-1].content)
            return resposta["messages"][-1].content
        else:
            print(str(resposta))
            return str(resposta)
    

    def agente_intencoes(self,query) :
        prompt_ref = self.prompts.prompt_reconhecimento_inten(query)
        agent = create_agent(self.llm,system_prompt=prompt_ref)
        response = agent.invoke({"input":prompt_ref})
        return self.verificar_resposta(response)


    def agente_empresas(self,query) :
        prompt_ref = self.prompts.prompt_reconhecimento_empresas(query)
        tools_ref = self.tools.ferramenta_busca_empresas(query)
        agent = create_agent(self.llm,tools=tools_ref,system_prompt=prompt_ref)
        response = agent.invoke({"input":prompt_ref})
        return self.verificar_resposta(response)


    def agente_datas(self,query) :
        prompt_ref = self.prompts.prompt_reconhecimento_data(query)
        agent = create_agent(self.llm,system_prompt=prompt_ref)
        response = agent.invoke({"input":prompt_ref})
        return self.verificar_resposta(response)


    def agente_noticias_01(self,query) :
        prompt_ref = self.prompts.prompt_agente_noticias_01(query)
        tools_ref = self.tools.ferramenta_busca_noticias(query) + self.tools.ferramenta_busca_empresas(query)
        agent = create_agent(self.llm,tools=tools_ref,system_prompt=prompt_ref)
        response = agent.invoke({"input":prompt_ref})
        return self.verificar_resposta(response)