import streamlit as st
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SerpAPIWrapper
from langchain.schema import HumanMessage
from langgraph.graph import StateGraph, END
from langsmith import trace
import logging
from typing import Dict, Any, Optional, TypedDict
from datetime import datetime

# ==================================================================================================
# 1. CONFIGURAÇÃO INICIAL (Logging e Variáveis de Ambiente)
# ==================================================================================================

# Configura o logging para exibir informações no console
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@st.cache_resource
def load_environment():
    """
    Carrega as variáveis de ambiente de um arquivo .env.
    É essencial para manter as chaves de API seguras e fora do código.
    """
    load_dotenv()
    return {
        'openai_api_key': os.getenv("OPENAI_API_KEY"),
        'serpapi_api_key': os.getenv("SERPAPI_API_KEY"),
        'langsmith_api_key': os.getenv("LANGSMITH_API_KEY")
    }

# ==================================================================================================
# 2. CONFIGURAÇÃO DAS FERRAMENTAS (LLM e Busca)
# ==================================================================================================

@st.cache_resource
def setup_tools(env_vars: Dict[str, str]):
    """
    Inicializa o Large Language Model (LLM) e a ferramenta de busca.
    O LLM é o cérebro da operação, e a ferramenta de busca coleta informações da web.
    """
    # Configura o LLM (GPT-4o-mini da OpenAI)
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7,
        api_key=env_vars.get('openai_api_key'),
        max_tokens=2000
    )

    # Configura a ferramenta de busca (SerpAPI)
    search_tool = SerpAPIWrapper(serpapi_api_key=env_vars.get('serpapi_api_key'))
    
    return llm, search_tool

# ==================================================================================================
# 3. DEFINIÇÃO DO WORKFLOW (Estado e Nós)
# ==================================================================================================

class MeetingState(TypedDict):
    """
    Define a estrutura de dados (estado) que flui através do workflow.
    Cada campo armazena uma parte da informação gerada em cada etapa.
    """
    company_name: str
    meeting_objective: str
    attendees: str
    duration: int
    focus_areas: str
    context_analysis: str
    industry_analysis: str
    strategy: str
    executive_brief: str
    timestamp: str

def validate_inputs(company: str, objective: str, attendees: str) -> Optional[str]:
    """Valida os inputs do usuário."""
    if not company.strip():
        return "Nome da empresa é obrigatório"
    if not objective.strip():
        return "Objetivo da reunião é obrigatório"
    if not attendees.strip():
        return "Lista de participantes é obrigatória"
    if len(company) < 2:
        return "Nome da empresa deve ter pelo menos 2 caracteres"
    return None

# --- Funções dos Nós do Grafo ---

def context_analysis_node(state: MeetingState) -> dict:
    """
    Nó 1: Analisa o contexto da empresa e da reunião.
    Busca notícias, produtos e serviços da empresa para criar um resumo inicial.
    """
    logger.info(f"Iniciando análise de contexto para: {state['company_name']}")
    try:
        query = f'"{state["company_name"]}" notícias recentes, produtos e serviços 2024 2025'
        search_results = search_tool.run(query)
        
        prompt = f"""
        Você é um analista de negócios sênior. Sua tarefa é analisar o contexto para uma reunião com a empresa '{state['company_name']}'.

        **DADOS DA REUNIÃO:**
        - Objetivo: {state['meeting_objective']}
        - Participantes: {state['attendees']}
        - Duração: {state['duration']} minutos

        **RESULTADOS DA PESQUISA WEB:**
        {search_results[:3000]}

        **INSTRUÇÃO:**
        Com base nos dados, gere uma análise de contexto concisa em markdown, incluindo:
        1.  **Perfil da Empresa:** Setor, porte e posicionamento de mercado.
        2.  **Notícias Relevantes:** Principais acontecimentos recentes.
        3.  **Produtos/Serviços Chave:** O que a empresa oferece.
        4.  **Relevância para a Reunião:** Como este contexto impacta o objetivo da reunião.
        """
        
        response = llm([HumanMessage(content=prompt)])
        logger.info("Análise de contexto concluída.")
        return {"context_analysis": response.content}
        
    except Exception as e:
        logger.error(f"Erro na análise de contexto: {e}")
        return {"context_analysis": f"⚠️ Falha ao analisar o contexto da empresa: {e}"}

def industry_analysis_node(state: MeetingState) -> dict:
    """
    Nó 2: Analisa a indústria e o mercado da empresa.
    Busca por tendências, competidores e análises de mercado.
    """
    logger.info("Iniciando análise de indústria.")
    try:
        industry_query = f"Análise de mercado e tendências para o setor da empresa '{state['company_name']}'"
        industry_results = search_tool.run(industry_query)
        
        prompt = f"""
        Como analista de mercado, sua tarefa é analisar a indústria da empresa '{state['company_name']}'.

        **CONTEXTO DA REUNIÃO:**
        - Objetivo: {state['meeting_objective']}

        **DADOS DE MERCADO (PESQUISA WEB):**
        {industry_results[:3000]}

        **INSTRUÇÃO:**
        Forneça uma análise da indústria em markdown, focando em:
        1.  **Panorama do Setor:** Tamanho, crescimento e características.
        2.  **Tendências Atuais:** Tecnológicas, de consumo ou regulatórias.
        3.  **Cenário Competitivo:** Principais concorrentes e seus diferenciais.
        4.  **Oportunidades e Ameaças (SWOT):** Fatores que podem impactar a reunião.
        """
        
        response = llm([HumanMessage(content=prompt)])
        logger.info("Análise de indústria concluída.")
        return {"industry_analysis": response.content}
        
    except Exception as e:
        logger.error(f"Erro na análise de indústria: {e}")
        return {"industry_analysis": f"⚠️ Falha ao analisar a indústria: {e}"}

def strategy_development_node(state: MeetingState) -> dict:
    """
    Nó 3: Desenvolve a estratégia e a agenda da reunião.
    Usa as análises anteriores para criar um plano de ação.
    """
    logger.info("Desenvolvendo estratégia da reunião.")
    try:
        prompt = f"""
        Você é um consultor estratégico. Sua missão é criar uma estratégia para a reunião com base nas análises.

        **ANÁLISE DE CONTEXTO:**
        {state.get('context_analysis', 'Não disponível')}

        **ANÁLISE DE INDÚSTRIA:**
        {state.get('industry_analysis', 'Não disponível')}

        **PARÂMETROS DA REUNIÃO:**
        - Duração: {state['duration']} minutos
        - Objetivo: {state['meeting_objective']}
        - Participantes: {state['attendees']}

        **INSTRUÇÃO:**
        Desenvolva uma estratégia de reunião em markdown, contendo:
        1.  **Agenda Detalhada:** Tópicos com tempo alocado (total: {state['duration']} min).
        2.  **Estratégia de Abordagem:** Mensagens-chave a serem comunicadas e perguntas a serem feitas.
        3.  **Plano de Ação e Próximos Passos:** O que fazer após a reunião.
        """
        
        response = llm([HumanMessage(content=prompt)])
        logger.info("Estratégia da reunião desenvolvida.")
        return {"strategy": response.content}
        
    except Exception as e:
        logger.error(f"Erro no desenvolvimento da estratégia: {e}")
        return {"strategy": f"⚠️ Falha ao desenvolver a estratégia: {e}"}

def executive_brief_node(state: MeetingState) -> dict:
    """
    Nó 4: Cria o briefing executivo final.
    Consolida todas as informações em um documento final e acionável.
    """
    logger.info("Criando o briefing executivo.")
    try:
        prompt = f"""
        Como assistente executivo, compile um briefing final para a reunião com '{state['company_name']}'.

        **DADOS COMPILADOS:**
        - Contexto: {state.get('context_analysis', 'Não disponível')}
        - Indústria: {state.get('industry_analysis', 'Não disponível')}
        - Estratégia: {state.get('strategy', 'Não disponível')}

        **INSTRUÇÃO:**
        Crie um briefing executivo completo e bem estruturado em markdown. O documento deve ser claro, conciso e visualmente organizado. Use emojis para destacar seções.

        # 📋 BRIEFING EXECUTIVO: Reunião com {state['company_name']}

        ## 🎯 1. RESUMO DA REUNIÃO
        - **Objetivo:** {state['meeting_objective']}
        - **Participantes:** {state['attendees']}
        - **Duração:** {state['duration']} minutos

        ## 🏢 2. CONTEXTO DA EMPRESA
        {state.get('context_analysis', 'Análise não disponível.')}

        ## 📊 3. ANÁLISE DE MERCADO
        {state.get('industry_analysis', 'Análise não disponível.')}

        ## 🚀 4. ESTRATÉGIA E AGENDA
        {state.get('strategy', 'Estratégia não disponível.')}
        """
        
        response = llm([HumanMessage(content=prompt)])
        logger.info("Briefing executivo finalizado.")
        return {"executive_brief": response.content}
        
    except Exception as e:
        logger.error(f"Erro na criação do briefing: {e}")
        return {"executive_brief": f"⚠️ Falha ao criar o briefing: {e}"}

# --- Construção do Grafo ---

@st.cache_resource
def build_workflow():
    """
    Constrói o grafo de execução (workflow) usando LangGraph.
    Define a sequência em que os nós (funções) serão executados.
    """
    workflow = StateGraph(MeetingState)
    
    # Adiciona os nós ao grafo
    workflow.add_node("context", context_analysis_node)
    workflow.add_node("industry", industry_analysis_node)
    workflow.add_node("strategy", strategy_development_node)
    workflow.add_node("brief", executive_brief_node)
    
    # Define as arestas (a ordem de execução)
    workflow.set_entry_point("context")
    workflow.add_edge("context", "industry")
    workflow.add_edge("industry", "strategy")
    workflow.add_edge("strategy", "brief")
    workflow.add_edge("brief", END)
    
    # Compila o grafo em um objeto executável
    return workflow.compile()

# ==================================================================================================
# 4. INTERFACE DO USUÁRIO (Streamlit)
# ==================================================================================================

def setup_sidebar(env_vars: Dict[str, str]):
    """Configura a barra lateral com instruções e status do sistema."""
    with st.sidebar:
        st.markdown("## 📚 Como Usar")
        st.markdown('''
        1.  **Configure as APIs:** Crie um arquivo `.env` na raiz do projeto com suas chaves de API:
            ```
            OPENAI_API_KEY="sua_chave_openai"
            SERPAPI_API_KEY="sua_chave_serpapi"
            LANGSMITH_API_KEY="sua_chave_langsmith" # Opcional
            ```
        2.  **Preencha os Campos:** Insira as informações da reunião nos campos ao lado.
        3.  **Execute:** Clique em "Preparar Reunião" para iniciar o processo.
        ''')
        
        st.markdown("---")
        st.markdown("## ⚙️ Status do Sistema")
        
        if env_vars.get('openai_api_key'):
            st.success("✅ OpenAI API conectada")
        else:
            st.error("❌ OpenAI API não configurada")
            
        if env_vars.get('serpapi_api_key'):
            st.success("✅ SerpAPI conectada")
        else:
            st.error("❌ SerpAPI não configurada")
            
        if env_vars.get('langsmith_api_key'):
            st.success("✅ LangSmith conectado")
        else:
            st.info("ℹ️ LangSmith não configurado")
            
        st.markdown("---")
        st.caption("🤖 Powered by LangChain & LangGraph")

# ==================================================================================================
# 5. EXECUÇÃO PRINCIPAL
# ==================================================================================================

if __name__ == "__main__":
    # Carrega configs e ferramentas
    env_vars = load_environment()
    llm, search_tool = setup_tools(env_vars)
    
    # --- Interface do Usuário ---
    st.set_page_config(page_title="AI Meeting Agent 📝", layout="wide", initial_sidebar_state="expanded")
    st.title("🤖 Agente IA para Preparação de Reuniões")
    
    setup_sidebar(env_vars)

    with st.container():
        st.subheader("📝 Informações da Reunião")
        col1, col2 = st.columns([2, 1])
        with col1:
            company_name = st.text_input("🏢 Nome da Empresa:", placeholder="Ex: Microsoft, Google...")
            meeting_objective = st.text_input("🎯 Objetivo da Reunião:", placeholder="Ex: Apresentar proposta de parceria...")
            attendees = st.text_area("👥 Participantes e Funções:", placeholder="""Ex:
• João Silva - CEO
• Maria Santos - Diretora de Vendas""", height=100)
        
        with col2:
            meeting_duration = st.selectbox("⏰ Duração (minutos):", options=[30, 45, 60, 90, 120], index=2)
            focus_areas = st.text_input("🔍 Áreas de Foco:", placeholder="Ex: Tecnologia, Preços, Prazos...")

    # --- Lógica de Execução ---
    st.markdown("---")
    
    # Verifica se as ferramentas essenciais estão prontas
    if not env_vars.get('openai_api_key') or not env_vars.get('serpapi_api_key'):
        st.error("❌ Configure as chaves de API da OpenAI e SerpAPI no arquivo .env para continuar.")
        st.stop()

    if st.button("🚀 Preparar Reunião", type="primary", use_container_width=True):
        # Validação dos inputs
        validation_error = validate_inputs(company_name, meeting_objective, attendees)
        if validation_error:
            st.warning(f"⚠️ {validation_error}")
        else:
            # Prepara o estado inicial para o workflow
            initial_state = {
                'company_name': company_name,
                'meeting_objective': meeting_objective,
                'attendees': attendees,
                'duration': meeting_duration,
                'focus_areas': focus_areas or "Nenhuma área específica definida",
                'context_analysis': '',
                'industry_analysis': '',
                'strategy': '',
                'executive_brief': '',
                'timestamp': datetime.now().isoformat()
            }
            
            # Compila e executa o workflow
            app = build_workflow()
            
            progress_bar = st.progress(0, text="Iniciando análise...")
            
            try:
                # Executa o grafo com rastreamento (se LangSmith estiver configurado)
                if env_vars.get('langsmith_api_key'):
                    with trace("meeting_preparation", inputs=initial_state):
                        result = app.invoke(initial_state)
                else:
                    result = app.invoke(initial_state)
                
                progress_bar.progress(100, text="Briefing finalizado!")

                # Exibe o resultado final
                st.success("✅ **Briefing preparado com sucesso!**")
                st.markdown("---")
                st.markdown(result["executive_brief"])
                
                # Botão de download
                st.download_button(
                    label="📥 Download do Briefing (MD)",
                    data=result["executive_brief"],
                    file_name=f"briefing_{company_name.lower().replace(' ', '_')}.md",
                    mime="text/markdown"
                )
                
            except Exception as e:
                st.error(f"❌ **Ocorreu um erro durante a preparação:** {e}")
                logger.error(f"Erro na execução do workflow: {e}")
            finally:
                if 'progress_bar' in locals():
                    progress_bar.empty()