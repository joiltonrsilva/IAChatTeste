# routers/zapi_webhook.py

import os
import requests
from fastapi import APIRouter, Request
from services.dialog_engine import handle_message  # renomeado de gerar_resposta
from utils.logger import log_event

# Carrega variáveis de ambiente Z-API
ZAPI_INSTANCE = os.getenv("ZAPI_INSTANCE", "")
ZAPI_TOKEN = os.getenv("ZAPI_TOKEN", "")
ZAPI_BASE_URL = f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{ZAPI_TOKEN}"

router = APIRouter(tags=["Z-API"], prefix="/zapi")


@router.post("/webhook")
async def receber_mensagem_zapi(request: Request):
    payload = await request.json()
    log_event("📩 PAYLOAD BRUTO ZAPI", payload)

    # 1) Checagens básicas
    numero = payload.get("phone")
    texto = payload.get("text", {}).get("message")
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

    # 4) Envia via Z-API
    send_url = f"{ZAPI_BASE_URL}/send-text"
    body = {"phone": numero, "message": conteudo}
    try:
        resp = requests.post(send_url, json=body, timeout=10)
        resp.raise_for_status()
        log_event("📤 Mensagem enviada Z-API", {"body": body, "response": resp.json()})
    except Exception as e:
        log_event("❌ Erro ao enviar Z-API", {"error": str(e), "body": body})

    return {"ok": True}
