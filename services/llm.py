import os
from langchain_ollama import OllamaLLM


def get_ollama_llm():
    '''
    Retorna uma instância do Ollama com o modelo e URL configurados.
    '''
    return OllamaLLM(
        model=os.getenv("LLM_MODEL", "gemma:2b"),
        base_url=os.getenv("OLLAMA_URL", "http://localhost:11434"),
    )