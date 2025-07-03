# services/copy_terminal.py

from random import choice

def gerar_copy_personalizada(lead: dict, produto: str) -> dict:
    nome = lead.get("nome", "Paciente")
    temperatura = lead.get("temperatura", "morno")
    contexto = lead.get("flags", {})

    tom = {
        "quente": "urgente e direto",
        "morno": "empático e assertivo",
        "frio": "suave e explicativo"
    }.get(temperatura, "neutro")

    cta_pool = [
        "Clique aqui para agendar",
        "Me avise quando quiser seguir",
        "Queremos te ajudar, vamos nessa?"
    ]

    mensagens = {
        "Pacote 3 Consultas": f"{nome}, esse pacote é ideal para quem precisa de acompanhamento próximo e decisões rápidas. A gente vai te guiar com segurança em cada passo.",
        "Plano Infantil": f"{nome}, esse plano cuida do acompanhamento completo da criança — focado em qualidade e cuidado contínuo.",
        "Pacote Gestacional": f"{nome}, este pacote cobre as fases mais importantes da gestação com atenção especializada.",
        "Plano Continuado": f"{nome}, você já teve contato com a gente antes. Com esse plano, garantimos consistência no cuidado e evolução segura.",
        "Consulta Avulsa": f"{nome}, podemos começar com uma consulta pontual para entender melhor sua situação e te orientar com precisão."
    }

    texto = mensagens.get(produto, f"{nome}, nossa sugestão é seguir com: {produto}")

    return {
        "texto": texto,
        "tom": tom,
        "chamada_para_acao": choice(cta_pool)
    }

# 🆕 Mock de envio da mensagem
def enviar_mensagem(numero: str, mensagem: str):
    print(f"[WHATSAPP MOCK] Enviando para {numero}: {mensagem}")
