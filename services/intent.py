import re

# Mapeamento robusto de intenções para palavras-chave (30+ variações cada)
INTENT_KEYWORDS = {
    "agendar": [
        "agendar", "marcar", "consulta", "horário", "agenda", "agendamento", "reservar",
        "disponibilidade", "reserva de horário", "marcação", "agendar consulta", "marcar consulta",
        "reservar horário", "quero agendar", "posso agendar", "quando posso agendar",
        "tem horário", "você tem horário", "dia de atendimento", "data disponível",
        "marcar atendimento", "agendar atendimento", "liberação de horário", "marcar horário",
        "reservar consulta", "agenda aberta", "vaga de horário", "reserva de data",
        "agendar para", "marcar para", "abrir agenda"
    ],
    "preco": [
        "quanto custa", "preço", "valor", "quanto é", "custa", "tabela de preços",
        "preço consulta", "valor consulta", "custo", "quanto pago", "qual o valor",
        "qual o preço", "preço serviço", "valor serviço", "quanto sai", "taxa",
        "tarifa", "quanto cobra", "cobrança", "quanto vai custar", "preço total",
        "valor total", "valor final", "custo final", "orçamento", "estimativa de valor",
        "orçamento consulta", "valor da consulta", "preço da consulta", "quanto fica"
    ],
    "cancelar": [
        "cancelar", "desmarcar", "cancelamento", "cancelar consulta", "desmarcar consulta",
        "quero cancelar", "posso cancelar", "como cancelar", "cancelar agendamento",
        "desmarcar agendamento", "cancelar horário", "desmarcar horário",
        "cancelamento de consulta", "solicito cancelamento", "preciso cancelar",
        "desistir", "anular", "anular consulta", "remover agendamento",
        "remover consulta", "cancelamento imediato", "não posso ir", "não irei",
        "liberar vaga", "liberar horário", "cancelar reserva", "pedido de cancelamento",
        "encerrar agendamento", "abortar consulta", "cancelamento definitivo"
    ]
}

# Intenção padrão quando nenhuma keyword for encontrada
def detectar_intencao(mensagem: str) -> str:
    """
    Analisa a mensagem do usuário e retorna a intenção detectada.
    Retorna:
        - chave da intenção (ex.: "agendar", "preco", "cancelar")
        - "nenhuma" caso nenhuma intenção seja encontrada
    """
    texto = mensagem.lower()
    # Itera pelas intenções e verifica se alguma keyword aparece na mensagem
    for intent, keywords in INTENT_KEYWORDS.items():
        for kw in keywords:
            if re.search(r"\b" + re.escape(kw) + r"\b", texto):
                return intent
    return "nenhuma"
