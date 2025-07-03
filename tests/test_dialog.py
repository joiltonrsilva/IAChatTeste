import os
import pytest
import redis
from fastapi.testclient import TestClient
from nora_ai.main import app

# Configurações de teste para Redis
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

@pytest.fixture(autouse=True)
def flush_redis():
    """
    Fixture que limpa o Redis antes de cada teste.
    """
    client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
    client.flushdb()
    yield
    client.flushdb()

@pytest.fixture()
def client():
    """
    TestClient do FastAPI para chamadas ao webhook.
    """
    return TestClient(app)

def post_message(client, phone, message):
    """
    Helper para enviar payload simulando a Z-API.
    """
    payload = {
        "fromMe": False,
        "type": "ReceivedCallback",
        "isGroup": False,
        "isNewsletter": False,
        "phone": phone,
        "text": {"message": message}
    }
    return client.post("/zapi/webhook", json=payload)

def test_simple_greeting(client):
    """
    Testa que NORA responde a saudação básica.
    """
    response = post_message(client, "5541999999999", "Oi, boa tarde!")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert "boa tarde" in data["resposta_enviada"].lower()

def test_agendamento_flow(client):
    """
    Testa fluxo de agendamento completo:
    1) Lead diz que quer agendar
    2) NORA pede data e horário
    3) Lead fornece data e horário válidos
    4) NORA confirma agendamento
    """
    phone = "5541999999998"
    # 1) Intenção de agendar
    r1 = post_message(client, phone, "Quero agendar uma consulta")
    assert r1.status_code == 200
    d1 = r1.json()
    assert "por favor me informe a data" in d1["resposta_enviada"].lower()

    # 2) Fornece data e horário válidos (conforme slots mock)
    r2 = post_message(client, phone, "2025-07-01 09:00")
    assert r2.status_code == 200
    d2 = r2.json()
    assert "capturados" in d2["resposta_enviada"].lower()

    # 3) Chamamos novamente para processar agendamento
    r3 = post_message(client, phone, "")  # mensagem vazia para acionar scheduler
    assert r3.status_code == 200
    d3 = r3.json()
    assert "confirmado" in d3["resposta_enviada"].lower()
    assert "09:00" in d3["resposta_enviada"]

    # Verifica no Redis se o slot foi removido
    client_redis = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
    remaining = client_redis.get(f"session:{phone}")
    assert remaining is not None

def test_intent_detection_preco(client):
    """
    Testa detecção de intenção de preço e resposta genérica do GPT.
    """
    response = post_message(client, "5541999999997", "Quanto custa uma consulta?")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert "custa" in data["resposta_enviada"].lower() or data["resposta_enviada"]
