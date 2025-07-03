# test_pipeline.py

from dotenv import load_dotenv
load_dotenv()  # 🔥 garante que SUPABASE_URL e SUPABASE_KEY sejam carregadas do .env

import asyncio
from services.product_pipeline import process_zapi_payload, process_google_form

async def main():
    # 1) Simula a primeira mensagem do lead
    payload_msg = {
        "phone": "5541999999999",
        "senderName": "Carla",
        "message": "Oi, estou tentando engravidar há um tempo e meu marido fez um espermograma com resultado ruim."
    }
    await process_zapi_payload(payload_msg)

    # 2) Simula a resposta do Google Forms
    payload_form = {
        "phone": "5541999999999",
        "respostas": {
            "flags": {"is_ttc": True, "bad_sperm": True},
            "temperatura": "quente",
            "score": 90
        }
    }
    await process_google_form(payload_form)

    # 3) Simula uma nova mensagem pós-formulário
    await process_zapi_payload({
        "phone": "5541999999999",
        "senderName": "Carla",
        "message": "Pronto, respondi!"
    })

if __name__ == "__main__":
    asyncio.run(main())
