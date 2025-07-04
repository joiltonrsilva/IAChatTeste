# routers/zapi_webhook.py

import os
import requests
from fastapi import APIRouter, Request
from services.dialog_engine import handle_message
from utils.logger import log_event

# Carrega variáveis de ambiente Z-API
ZAPI_INSTANCE = os.getenv("ZAPI_INSTANCE", "")
ZAPI_TOKEN = os.getenv("ZAPI_TOKEN", "")
ZAPI_BASE_URL = f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{ZAPI_TOKEN}"

router = APIRouter(tags=["Z-API"], prefix="/zapi")


@router.post("/webhook")
async def receber_mensagem_zapi(request: Request):
    # 0) Recebe e loga o payload cru
    payload = await request.json()
    log_event("📩 PAYLOAD BRUTO ZAPI", payload)

    # 1) Extrai número e texto, suportando ambos formatos
    numero = None
    texto = None

    # → Novo formato Z-API: { "messages": [ { "from": "...", "text": { "body": "..." } } ] }
    msgs = payload.get("messages")
    if isinstance(msgs, list) and len(msgs) > 0:
        msg = msgs[0]
        numero = msg.get("from")
        texto = msg.get("text", {}).get("body")

    # → Fallback legado: { "phone": "...", "text": { "message": "..." } }
    if not numero or not texto:
        numero = payload.get("phone") or numero
        texto = payload.get("text", {}).get("message") or texto

    # Se ainda faltar algo, rejeita
    if not numero or not texto:
        return {"ok": False, "motivo": "Payload inválido"}

    log_event(f"🔹 Mensagem recebida de {numero}", texto)

    # 2) Processa a mensagem (NLP, intents, scheduler etc.)
    resposta = await handle_message(numero, texto, payload)

    # 3) Normaliza o conteúdo a enviar
    if isinstance(resposta, dict):
        conteudo = resposta.get("mensagem", "")
    else:
        conteudo = str(resposta)

    # 4) Envia via Z-API com endpoint corrigido
    send_url = f"{ZAPI_BASE_URL}/send-messages"  # corrigido de /send-text → /send-messages
    body = {"phone": numero, "message": conteudo}
    try:
        resp = requests.post(send_url, json=body, timeout=10)
        resp.raise_for_status()
        log_event("📤 Mensagem enviada Z-API", {"body": body, "response": resp.json()})
    except Exception as e:
        log_event("❌ Erro ao enviar Z-API", {"error": str(e), "body": body})

    return {"ok": True}
