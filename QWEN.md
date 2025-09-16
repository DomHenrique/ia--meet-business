# AI Meeting Preparation Agent

## Project Overview

This project is a Streamlit-based AI application designed to help users prepare for business meetings. It leverages OpenAI's GPT models and web search tools (SerpAPI or DuckDuckGo) to automatically generate comprehensive meeting briefings.

### Core Functionality

1.  **User Input:** Collects essential meeting details:
    *   Company name
    *   Meeting objective
    *   Attendees and their roles
    *   Meeting duration
    *   Focus areas
2.  **Automated Research & Analysis:**
    *   **Context Analysis:** Gathers and analyzes recent information about the target company.
    *   **Industry Analysis:** Provides insights into the company's industry, market trends, and competitors.
3.  **Strategy Development:** Creates a detailed meeting strategy, including a timeboxed agenda and key talking points.
4.  **Executive Briefing:** Compiles all information into a final, concise, and actionable executive briefing document in Markdown format.
5.  **Download:** Allows the user to download the generated briefing.

### Technologies Used

*   **Framework:** Streamlit (for the web UI)
*   **AI/LLM:** LangChain, LangGraph, OpenAI (GPT-4o-mini)
*   **Web Search:** SerpAPI (primary) / DuckDuckGo Search (fallback)
*   **Observability:** LangSmith (optional)
*   **Environment Management:** python-dotenv
*   **Logging:** Python's built-in `logging` module

## Running the Application

1.  **Prerequisites:**
    *   Python 3.7+
    *   An OpenAI API key (mandatory).
    *   (Optional) A SerpAPI key for enhanced web search.
    *   (Optional) LangSmith API key for tracing.
2.  **Setup:**
    *   Create a virtual environment: `python -m venv venv`
    *   Activate it: `source venv/bin/activate` (Linux/macOS) or `venv\Scripts\activate` (Windows)
    *   Install dependencies (note: `requeriments.txt` is currently empty, so dependencies need to be installed manually or inferred from `app.py` imports):
        *   `streamlit`
        *   `python-dotenv`
        *   `langchain`
        *   `langchain-openai`
        *   `langchain-community`
        *   `langgraph`
        *   `langsmith`
        *   Example install command: `pip install streamlit python-dotenv langchain langchain-openai langchain-community langgraph langsmith`
3.  **Configuration:**
    *   Create a `.env` file in the project root with your API keys:
        ```
        OPENAI_API_KEY=your_openai_api_key
        SERPER_API_KEY=your_serper_api_key # Optional
        LANGCHAIN_TRACING_V2=true # Optional
        LANGCHAIN_API_KEY=your_langchain_api_key # Optional
        LANGCHAIN_PROJECT=your_project_name # Optional
        ```
    *   An example `.env` file is already present, but you should replace the keys with your own.
4.  **Execution:**
    *   Run the application: `streamlit run app.py`
    *   Access the application in your browser (usually `http://localhost:8501`).

## Development Conventions

*   **Structure:** The main application logic resides in `app.py`. It uses a stateful workflow managed by `LangGraph`.
*   **Caching:** Streamlit's `@st.cache_resource` decorator is used for loading environment variables and setting up tools to improve performance.
*   **Error Handling:** Basic try-except blocks are used around LLM calls and workflow execution to catch and display errors to the user.
*   **Logging:** Python's `logging` module is used for tracking application activity.
*   **Environment Variables:** API keys and other configurations are managed using `python-dotenv`.
*   **UI/UX:** The Streamlit UI is designed to be user-friendly with clear input sections, status indicators, progress tracking, and a sidebar with instructions.