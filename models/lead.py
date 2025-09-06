# models/lead.py
from typing import Optional
import os
import json
from supabase import create_client, Client
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Captura variáveis de ambiente
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Validação explícita das variáveis
if not SUPABASE_URL or not SUPABASE_KEY:
    raise EnvironmentError(
        f"[ERRO] Variáveis de ambiente inválidas: SUPABASE_URL={SUPABASE_URL}, SUPABASE_KEY={'set' if SUPABASE_KEY else 'missing'}"
    )

# Criação do cliente Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_lead(phone: str) -> Optional[dict]:
    """
    Busca o lead no Supabase pelo número de telefone.
    Se não encontrar, retorna None.
    """
    try:
        response = supabase.table("leads").select("*").eq("numero", phone).single().execute()
        return response.data if response.data else None
    except Exception as e:
        print(f"[DEBUG] Lead não encontrado para {phone} ou erro ao buscar: {e}")
        return None


def create_lead(phone: str) -> dict:
    """
    Cria um novo lead no Supabase com estrutura padrão.
    """
    novo_lead = {
        "numero": phone,
        "nome": "",
        "flags": [],
        "score": 0,
        "temperatura": "morno",
        "formulario_respondido": False,
        "produto_escolhido": None,
        "historico": "",
        "updated_at": datetime.utcnow().isoformat()
    }
    response = supabase.table("leads").insert(novo_lead).execute()
    if response.data:
        return response.data[0]
    else:
        raise RuntimeError(f"[ERRO] Falha ao criar lead no Supabase: {response}")


def update_lead(phone: str, updates: dict) -> dict:
    """
    Atualiza um lead existente no Supabase de forma segura.
    - Converte dicionários em JSON
    - Filtra apenas colunas existentes
    """
    updates["updated_at"] = datetime.utcnow().isoformat()

    # 1) Busca uma linha existente para pegar as colunas válidas
    response = supabase.table("leads").select("*").eq("numero", phone).limit(1).execute()
    if not response.data:
        raise ValueError(f"Lead com telefone {phone} não encontrado.")

    existing_columns = set(response.data[0].keys())

    # 2) Filtra updates para apenas colunas existentes e converte dicts em JSON
    safe_updates = {}
    for k, v in updates.items():
        if k in existing_columns:
            safe_updates[k] = json.dumps(v) if isinstance(v, dict) else v

    if not safe_updates:
        raise ValueError(f"Nenhuma coluna válida para atualizar para o lead {phone}.")

    # 3) Atualiza a tabela
    try:
        response = supabase.table("leads").update(safe_updates).eq("numero", phone).execute()
        if response.data:
            return response.data[0]
        else:
            raise ValueError(f"Falha na atualização do lead {phone}: {response}")
    except Exception as e:
        raise ValueError(f"Erro ao atualizar lead {phone}: {str(e)}")
