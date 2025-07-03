# services/choose_product.py

def escolher_produto(lead: dict):
    """
    Decide o produto ideal com base no perfil do lead.

    Parâmetros:
        lead (dict): dicionário com informações do lead, como flags, score e histórico.

    Retorno:
        (str) nome do produto recomendado
        (list) critérios utilizados na decisão
    """
    flags = lead.get("flags", {})
    score = lead.get("score", 0)
    historico = lead.get("has_previous_interaction", False)

    # 1. Flags obrigatórias
    if flags.get("is_ttc") or flags.get("bad_sperm"):
        return "Pacote 3 Consultas", ["is_ttc", "bad_sperm"]

    if flags.get("is_child8"):
        return "Plano Infantil", ["is_child8"]

    if flags.get("is_gest"):
        return "Pacote Gestacional", ["is_gest"]

    # 2. Menopausa → copy diferenciada, mas volta ao fluxo comum
    if flags.get("menopausa"):
        pass  # Trataremos a copy depois

    # 3. Score + histórico
    if score >= 70 and historico:
        return "Plano Continuado", ["score ≥ 70", "com histórico"]

    return "Consulta Avulsa", ["score < 70", "ou sem histórico"]
