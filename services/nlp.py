# services/nlp.py

import asyncio
from services.choose_product import escolher_produto
from services.llm import get_ollama_llm  # sua função que retorna o LlamaLLM configurado
import json

# ──────────────────────────────────────────────────────────────────────────────
# 🧠 Terminal 1 — NORA_PERFIL
# Extrai flags, urgência e temperatura emocional
# ──────────────────────────────────────────────────────────────────────────────
llm_perfil = get_ollama_llm()

async def analise_perfil(mensagem: str) -> dict:
    prompt = f"""
Você é um analista clínico. A partir de mensagens de pacientes, extraia:
- flags relevantes (tentante, gestante, menopausa, criança 8 anos, espermograma ruim)
- urgência (score de 0 a 100)
- temperatura emocional (quente, morno ou frio)
Responda em JSON com as chaves: flags, urgencia, temperatura.

Mensagem do paciente: {mensagem}
"""
    try:
        resposta = await asyncio.to_thread(llm_perfil.invoke, prompt)
        return json.loads(resposta)
    except Exception as e:
        return {
            "flags": {},
            "urgencia": 0,
            "temperatura": "morno",
            "erro": str(e)
        }


# ──────────────────────────────────────────────────────────────────────────────
# 📝 Terminal 2 — NORA_COPY
# Gera copy emocional com base no produto e perfil
# ──────────────────────────────────────────────────────────────────────────────
llm_copy = get_ollama_llm()

async def gerar_copy(produto: str, temperatura: str, nome: str) -> str:
    prompt = f"""
Paciente: {nome}
Temperatura emocional: {temperatura}
Produto recomendado: {produto}

Gere uma mensagem empática, clara e persuasiva em até 3 parágrafos,
explicando por que esse produto é ideal. Termine com uma chamada para ação.
"""
    resposta = await asyncio.to_thread(llm_copy.invoke, prompt)
    return str(resposta).strip()


# ──────────────────────────────────────────────────────────────────────────────
# 🧮 Terminal 3 — NORA_DECISAO (IA)
# Decide o produto ideal com base em Llama
# ──────────────────────────────────────────────────────────────────────────────
llm_decisao = get_ollama_llm()

async def decidir_produto_ia(score: int, flags: dict, historico: bool) -> str:
    prompt = f"""
Score de urgência: {score}
Flags do paciente: {flags}
Histórico prévio (has_previous_interaction): {historico}

Escolha e retorne apenas o nome de um dos seguintes produtos:
- Pacote 3 Consultas
- Plano Infantil
- Pacote Gestacional
- Plano Continuado
- Consulta Avulsa
"""
    resposta = await asyncio.to_thread(llm_decisao.invoke, prompt)
    return str(resposta).strip()


# ──────────────────────────────────────────────────────────────────────────────
# 🎯 Função principal de decisão para o pipeline (regra interna)
# Avaliar produto usando choose_product.py
# ──────────────────────────────────────────────────────────────────────────────
def avaliar_produto(score: int, flags: list, historico: str) -> str:
    lead = {
        "score": score,
        "flags": {f: True for f in flags},
        "has_previous_interaction": bool(historico and historico.strip())
    }
    produto, _criterios = escolher_produto(lead)
    return produto
