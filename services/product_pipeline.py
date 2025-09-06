# services/product_pipeline.py

from models.lead import get_lead, create_lead, update_lead
from services.choose_product import escolher_produto
from services.copy_terminal import enviar_mensagem
from services.nlp import analise_perfil, avaliar_produto, gerar_copy
from utils.logger import log_event
import random

# Frases que indicam “formulário preenchido”
RESPONDI_KEYWORDS = ["preenchi", "respondi", "enviei o formulário", "já preenchi"]

async def process_zapi_payload(payload: dict):
    numero = payload.get("phone")
    texto = payload.get("message", "")

    log_event("📩 Mensagem recebida do WhatsApp", {"numero": numero, "texto": texto})

    # 1) Carrega ou cria lead
    lead = get_lead(numero)
    if not lead:
        lead = create_lead(numero)
        # 🚨 DEBUG: imprime no terminal o que veio do Supabase / do dicionário
        log_event("🚨 DEBUG: Lead criado com dados", lead)

        lead["formulario_respondido"] = False
        lead["etapa"] = "inicial"
        log_event("👤 Novo lead criado", {"numero": numero})

    etapa = lead.get("etapa", "inicial")

    # 2) Se estivermos aguardando resposta do formulário…
    if etapa == "aguardando_form":
        if any(k in texto.lower() for k in RESPONDI_KEYWORDS):
            # Marca como respondido e avança
            lead["formulario_respondido"] = True
            lead["etapa"] = "produto"
            update_lead(numero, lead)
            log_event("✅ Formulário sinalizado como respondido", {"numero": numero})
        else:
            # Ainda não entendeu que preencheu
            enviar_mensagem(
                numero,
                "Ops, não consegui confirmar se você já respondeu. "
                "Assim que preencher o formulário, me avisa aqui!"
            )
            return

    # 3) Se ainda não respondeu ao formulário, roda NLP e pede o link
    if not lead.get("formulario_respondido"):
        perfil_resultado = await analise_perfil(texto)
        lead.update(perfil_resultado)
        log_event("🧠 Perfil analisado", perfil_resultado)

        link = f"https://forms.gle/{random.randint(1000,9999)}-fake"
        enviar_mensagem(
            numero,
            f"Perfeito! Antes de continuar, responde esse formulário rapidinho? 💜\n{link}"
        )
        lead["etapa"] = "aguardando_form"
        update_lead(numero, lead)
        log_event("📮 Formulário enviado", {"numero": numero})
        return

    # 4) Etapa de produto: já preencheu
    produto = avaliar_produto(
        score=lead.get("score", 0),
        flags=lead.get("flags", []),
        historico=lead.get("historico", "")
    )
    lead["produto_escolhido"] = produto
    log_event("📦 Produto definido", {"produto": produto})

    # 5) Gera a copy final e envia
    texto_final = await gerar_copy(
        produto,
        lead.get("temperatura", "morno"),
        lead.get("nome", "")
    )
    enviar_mensagem(numero, texto_final)
    log_event("📤 Resposta enviada", {"texto": texto_final})

    # 6) Finaliza o lead
    lead["etapa"] = "finalizado"
    update_lead(numero, lead)


# 📥 Google Forms (simulado via Webhook)
async def process_google_form(payload: dict):
    numero = payload.get("phone")
    respostas = payload.get("respostas", {})

    lead = get_lead(numero)
    if not lead:
        lead = create_lead(numero)

    # Salva que o formulário foi respondido e grava respostas
    lead["formulario_respondido"] = True
    lead["etapa"] = "produto"
    lead["idade"] = respostas.get("idade")
    lead["tentante"] = respostas.get("tentante")
    lead["menopausa"] = respostas.get("menopausa")
    lead["historico"] = respostas.get("historico", "")

    # Monta flags e score baseados nas respostas
    lead["flags"] = []
    if lead["tentante"] == "sim":
        lead["flags"].append("tentante")
    if lead["menopausa"] == "sim":
        lead["flags"].append("menopausa")

    lead["score"] = 80 if "tentante" in lead["flags"] else 40

    log_event("📋 Formulário processado", {"numero": numero, "respostas": respostas})
    update_lead(numero, lead)
