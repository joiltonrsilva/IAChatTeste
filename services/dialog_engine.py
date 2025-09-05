import os
import re
from openai import AsyncOpenAI
from core.sessions import load_session, append_message, save_session
from services.intent import detectar_intencao
from services.scheduler import processar_agendamento

# Cliente OpenAI assíncrono para fallback GPT
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_KEY_COPY"))


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
    Fallback ao GPT-4o para conversas gerais não relacionadas a agendamento.
    """
    session = await load_session(phone_number)
    session_history = session.get("history", [])

    if os.getenv('MOCK_OPENAI', '0') == '1':
        mock_response = f'[MOCK] mensagem: {user_message}'
        await append_message(phone_number, "assistant", mock_response)
        return mock_response
    # Monta prompt com histórico + mensagem atual
    messages = build_multi_turn_prompt(session_history + [{"role": "user", "content": user_message}])
    try:
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=600,
            temperature=0.7,
        )
        assistant_response = response.choices[0].message.content.strip()
    except Exception as e:
        assistant_response = f'[ERRO] {str(e)}'

    # Salva no histórico
    await append_message(phone_number, "assistant", assistant_response)
    return assistant_response


async def handle_message(phone_number: str, user_message: str, payload: dict) -> dict | str:
    """
    Roteia mensagens:
    - captura data/horário
    - detecta intenção
    - para 'agendar', chama scheduler
    - senão, fallback GPT
    """
    # 1) Carrega e atualiza histórico da sessão
    session = await load_session(phone_number)
    session_history = session.get("history", [])
    await append_message(phone_number, "user", user_message)

    # 2) Captura data e horário padrão se presentes
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

    # 3) Detecta intenção via intent.py
    intencao = detectar_intencao(user_message)

    # 4) Fluxo de agendamento
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

        # Chama o scheduler (distância default 0 km)
        resultado = await processar_agendamento(phone_number, data, horario, distancia_km=0)
        await append_message(phone_number, "assistant", resultado.get("mensagem", ""))
        await save_session(phone_number, session)
        return resultado

    # 5) Fluxo padrão via GPT
    resposta_gpt = await gerar_resposta_fallback(phone_number, user_message)
    return resposta_gpt

