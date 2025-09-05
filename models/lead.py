# models/lead.py
from typing import Optional
import os
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
    Atualiza um lead existente no Supabase.
    """
    updates["updated_at"] = datetime.utcnow().isoformat()
    response = supabase.table("leads").update(updates).eq("numero", phone).execute()
    if response.data:
        return response.data[0]
    else:
        raise ValueError(f"Lead com telefone {phone} não encontrado ou falha na atualização: {response}")
