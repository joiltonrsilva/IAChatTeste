# services/scheduler.py

import os
import datetime
from typing import Optional
from supabase import create_client, Client

# ————— Supabase —————
SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ————— Slots simulados por dia —————
# Ex.: slots["2025-07-01"] = ["09:00", "10:00", ...]
slots: dict[str, list[str]] = {
    "2025-07-01": ["09:00", "10:00", "14:00"],
    "2025-07-02": ["11:00", "15:00"],
}

# ————— Validação de pacote obrigatório —————
async def validar_pacote_obrigatorio(lead_id: str) -> bool:
    """
    Verifica na tabela 'leads' se o lead (campo 'numero') possui
    'produto_escolhido' preenchido (indicando pacote adquirido).
    """
    resp = (
        supabase
        .table("leads")
        .select("produto_escolhido")
        .eq("numero", lead_id)
        .single()
        .execute()
    )
    if resp.error or resp.data is None:
        return False
    produto = resp.data.get("produto_escolhido", "")
    return bool(produto and produto.strip())

# ————— Disponibilidade e reserva de slots —————
async def verificar_disponibilidade(data: str, horario: str) -> bool:
    return horario in slots.get(data, [])

async def reservar_slot(data: str, horario: str) -> bool:
    if await verificar_disponibilidade(data, horario):
        slots[data].remove(horario)
        return True
    return False

async def sugerir_proximo_slot(data: str) -> Optional[str]:
    disponiveis = slots.get(data, [])
    return disponiveis[0] if disponiveis else None

# ————— Geração de link de pagamento (stub) —————
async def gerar_link_pagamento(
    lead_id: str, data: str, horario: str
) -> str:
    """
    Stub para integração com Stripe ou Cielo.
    Substituir por chamada real à API de pagamentos.
    """
    return (
        f"https://pagamento.gateway/checkout?"
        f"lead={lead_id}&data={data}&hora={horario}"
    )

# ————— Agendamento Inteligente —————
async def processar_agendamento(
    lead_id: str,
    data: str,
    horario: str,
    distancia_km: float
) -> dict:
    """
    1) Verifica pacote obrigatório.
    2) Verifica dia da semana (Seg/Ter/6ª).
    3) Determina modalidade (online/presencial) conforme distância.
    4) Tenta reservar slot:
       - slot livre  → reserva preliminar + gera link de pagamento
       - ocupado     → sugere próximo horário
       - sem slots   → informa indisponibilidade da data
    """
    # 1) Pacote
    if not await validar_pacote_obrigatorio(lead_id):
        return {
            "status": "erro_pacote",
            "mensagem": (
                "🚫 Para agendar sua consulta, é necessário adquirir um de nossos pacotes.\n"
                "Confira aqui: https://seusite.com/pacotes"
            )
        }

    # 2) Dia da semana
    try:
        dia = datetime.datetime.strptime(data, "%Y-%m-%d").weekday()
    except ValueError:
        return {
            "status": "data_invalida",
            "mensagem": "Formato de data inválido. Use YYYY-MM-DD."
        }

    if dia not in (0, 1, 4):  # 0=Segunda,1=Terça,4=Sexta
        return {
            "status": "dia_invalido",
            "mensagem": "Atendemos somente nas segundas, terças e sextas."
        }

    # 3) Modalidade
    if dia == 4 and distancia_km <= 150:
        modalidade = "presencial"
    else:
        modalidade = "online"

    # 4) Reserva / sugestão
    if await reservar_slot(data, horario):
        link = await gerar_link_pagamento(lead_id, data, horario)
        return {
            "status": "preliminar",
            "modalidade": modalidade,
            "mensagem": (
                f"✅ Reserva preliminar efetuada para {data} às {horario} "
                f"({modalidade}).\n"
                f"Para confirmar, efetue o pagamento aqui:\n{link}"
            )
        }

    # horário ocupado
    proximo = await sugerir_proximo_slot(data)
    if proximo:
        return {
            "status": "sugestao",
            "mensagem": (
                f"⏳ {horario} já foi ocupado. "
                f"Posso agendar para {proximo} ({modalidade})?"
            )
        }

    # sem slots na data
    return {
        "status": "indisponivel",
        "mensagem": (
            f"❌ Não há mais horários disponíveis em {data}. "
            "Deseja tentar outra data?"
        )
    }
