import os
import re

from core.sessions import load_session, append_message, save_session
from services.intent import detectar_intencao
from services.scheduler import processar_agendamento
from services.llm import get_ollama_llm
from services.memory import get_memory_for_user
from langchain.schema import HumanMessage
from services.scheduler import processar_agendamento

MOCK_OPENAI = os.getenv("MOCK_OPENAI", "0") == "1"

def build_multi_turn_prompt(session_history: list) -> list:
    """
    Monta a lista de mensagens no formato Chat Completion para o GPT,
    baseada no histórico da sessão + instrução do sistema.
    """
    messages = [
        {
            "role": "system",
            "content": (
                "Você é a NORA, uma assistente empática e precisa. "
                "Ajude os leads no processo de agendamento, escolha de produtos e esclarecimento de dúvidas, "
                "sempre mantendo um tom humano, acolhedor e objetivo."
            )
        }
    ]

    # Inclui as últimas 10 interações no histórico
    for msg in session_history[-10:]:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    return messages


async def gerar_resposta_fallback(phone_number: str, user_message: str) -> str:
    """
    Gera uma resposta fallback usando LLaMA local.
    - Carrega histórico da sessão do Supabase
    - Atualiza histórico com a mensagem do usuário
    - Gera resposta com LLaMA
    - Salva resposta no histórico
    - Suporta MOCK_OPENAI=1 para testes
    """
    # 1) Mock para testes
    if MOCK_OPENAI:
        mock_response = f"[MOCK] mensagem: {user_message}"
        await append_message(phone_number, "assistant", mock_response)
        return mock_response

    # 2) Carrega sessão/histórico
    session = await load_session(phone_number)
    session_history = session.get("history", [])

    # 3) Inicializa o LLaMA local
    llm = get_ollama_llm()

    # 4) Monta o prompt a partir do histórico + nova mensagem
    # Aqui você pode adaptar conforme o que LLaMA espera
    # Exemplo: lista de mensagens concatenadas
    prompt = ""
    for msg in session_history:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        prompt += f"{role}: {content}\n"
    prompt += f"user: {user_message}\nassistant:"

    # 5) Gera resposta com LLaMA (chamada síncrona)
    # Se estiver usando a versão async, adapte removendo await
    resposta = llm.invoke(prompt)  # invoke retorna str

    # 6) Atualiza histórico no Supabase
    await append_message(phone_number, "assistant", resposta)

    return resposta


async def handle_message(phone_number: str, user_message: str, payload: dict) -> dict | str:
    """
    Roteia mensagens:
    - captura data/horário
    - detecta intenção
    - para 'agendar', chama scheduler
    - senão, fallback LLaMA
    """
    # 1️⃣ Carrega e atualiza histórico da sessão
    session = await load_session(phone_number)
    await append_message(phone_number, "user", user_message)

    # 2️⃣ Captura data e horário padrão se presentes
    date_match = re.search(r"\d{4}-\d{2}-\d{2}", user_message)
    time_match = re.search(r"\b([01]?\d|2[0-3]):[0-5]\d\b", user_message)
    if date_match and time_match:
        data = date_match.group()
        horario = time_match.group()
        session["data"] = data
        session["horario"] = horario
        await append_message(phone_number, "assistant", f"Data {data} e horário {horario} capturados.")
        await save_session(phone_number, session)
        return f"Data {data} e horário {horario} capturados."

    # 3️⃣ Detecta intenção via intents
    intencao = detectar_intencao(user_message)

    # 4️⃣ Fluxo de agendamento
    if intencao == "agendar":
        data = session.get("data")
        horario = session.get("horario")
        if not data or not horario:
            pergunta = (
                "Claro! Para agendarmos, por favor me informe a data no formato AAAA-MM-DD "
                "e o horário no formato HH:MM que você deseja."
            )
            await append_message(phone_number, "assistant", pergunta)
            return pergunta

        resultado = await processar_agendamento(phone_number, data, horario, distancia_km=0)
        await append_message(phone_number, "assistant", resultado.get("mensagem", ""))
        await save_session(phone_number, session)
        return resultado

    # 5️⃣ Fluxo padrão via LLaMA local
    resposta_llama = await gerar_resposta_fallback(phone_number, user_message)
    return resposta_llama

