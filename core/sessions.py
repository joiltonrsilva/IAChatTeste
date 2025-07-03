# core/sessions.py

import os
import json
import redis
from datetime import datetime, timedelta

# Configuração do Redis
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
SESSION_TTL = 60 * 60  # Tempo de expiração: 1 hora

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True
)

def get_session_key(phone_number: str) -> str:
    """
    Retorna a chave única de sessão para cada lead baseado no telefone.
    """
    return f"session:{phone_number}"

async def load_session(phone_number: str) -> dict:
    """
    Carrega a sessão do Redis. Se não existir, retorna um dicionário vazio.
    """
    key = get_session_key(phone_number)
    session_data = redis_client.get(key)
    if session_data:
        return json.loads(session_data)
    return {"history": [], "created_at": datetime.utcnow().isoformat()}

async def save_session(phone_number: str, session: dict):
    """
    Salva/atualiza a sessão no Redis com TTL.
    """
    key = get_session_key(phone_number)
    redis_client.setex(key, SESSION_TTL, json.dumps(session))

async def append_message(phone_number: str, role: str, content: str):
    """
    Adiciona uma mensagem ao histórico da sessão.
    """
    session = await load_session(phone_number)
    session["history"].append({
        "role": role,          # "user" ou "assistant"
        "content": content,
        "timestamp": datetime.utcnow().isoformat()
    })
    await save_session(phone_number, session)

async def clear_session(phone_number: str):
    """
    Remove a sessão do Redis (ex.: após lead finalizado).
    """
    key = get_session_key(phone_number)
    redis_client.delete(key)
