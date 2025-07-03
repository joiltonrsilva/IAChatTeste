# services/nlp.py

import os
from openai import AsyncOpenAI
from services.choose_product import escolher_produto

# ──────────────────────────────────────────────────────────────────────────────
# Configuração dos 3 terminais OpenAI
# ──────────────────────────────────────────────────────────────────────────────
client_perfil  = AsyncOpenAI(api_key=os.getenv("OPENAI_KEY_PERFIL"))
client_copy    = AsyncOpenAI(api_key=os.getenv("OPENAI_KEY_COPY"))
client_decisao = AsyncOpenAI(api_key=os.getenv("OPENAI_KEY_DECISAO"))


# ──────────────────────────────────────────────────────────────────────────────
# 🧠 Terminal 1 — NORA_PERFIL
# Extrai flags, urgência e temperatura emocional
# ──────────────────────────────────────────────────────────────────────────────
async def analise_perfil(mensagem: str) -> dict:
    response = await client_perfil.chat.completions.create(
        model="gpt-3.5-turbo",
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": (
                    "Você é um analista clínico. A partir de mensagens de pacientes, extraia:\n"
                    "- flags relevantes (tentante, gestante, menopausa, criança 8 anos, espermograma ruim)\n"
                    "- urgência (score de 0 a 100)\n"
                    "- temperatura emocional (quente, morno ou frio).\n"
                    "Responda em JSON com as chaves: flags, urgencia, temperatura_emocional."
                )
            },
            {"role": "user", "content": mensagem}
        ]
    )

    try:
        content = response.choices[0].message.content.strip()
        # Em produção, use json.loads em vez de eval
        return eval(content) if isinstance(content, str) else content
    except Exception as e:
        return {
            "flags": {},
            "urgencia": 0,
            "temperatura_emocional": "morno",
            "erro": str(e)
        }


# ──────────────────────────────────────────────────────────────────────────────
# 📝 Terminal 2 — NORA_COPY
# Gera copy emocional com base no produto e perfil
# ──────────────────────────────────────────────────────────────────────────────
async def gerar_copy(produto: str, temperatura: str, nome: str) -> str:
    prompt = f"""
Paciente: {nome}
Temperatura emocional: {temperatura}
Produto recomendado: {produto}

Gere uma mensagem empática, clara e persuasiva em até 3 parágrafos,
explicando por que esse produto é ideal. Termine com uma chamada para ação.
"""
    response = await client_copy.chat.completions.create(
        model="gpt-4o",
        temperature=0.9,
        messages=[
            {"role": "system", "content": "Você é um redator empático e persuasivo."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()


# ──────────────────────────────────────────────────────────────────────────────
# 🧮 Terminal 3 — NORA_DECISAO (IA)
# Decide o produto ideal com base em GPT (opcional)
# ──────────────────────────────────────────────────────────────────────────────
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
    response = await client_decisao.chat.completions.create(
        model="gpt-4o",
        temperature=0.5,
        messages=[
            {
                "role": "system",
                "content": "Você é um sistema clínico que decide o produto ideal com base em lógica objetiva."
            },
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()


# ──────────────────────────────────────────────────────────────────────────────
# 🎯 Função principal de decisão para o pipeline (regra interna)
# Avaliar produto usando choose_product.py
# ──────────────────────────────────────────────────────────────────────────────
async def avaliar_produto(score: int, flags: list, historico: str) -> str:
    """
    Constrói um objeto temporário de lead e delega a decisão à função de regras puras.
    - score: int
    - flags: lista de nomes de flags (ex: ["is_ttc", "bad_sperm"])
    - historico: string (pode estar vazia)
    """
    lead = {
        "score": score,
        # converte lista em dict com True para cada flag
        "flags": {f: True for f in flags},
        "has_previous_interaction": bool(historico and historico.strip())
    }
    produto, _criterios = escolher_produto(lead)
    return produto
