# test_pipeline_supabase.py

import asyncio
from services.product_pipeline import process_zapi_payload, process_google_form

async def main():
    print("🔹 Etapa 1) Mensagem inicial do WhatsApp")
    await process_zapi_payload({
        "phone": "5541999999999",
        "senderName": "Carla",
        "message": "Oi, estou tentando engravidar há um tempo e meu marido fez um espermograma com resultado ruim."
    })

    print("\n🔹 Etapa 2) Simulação de envio do Forms")
    await process_google_form({
        "phone": "5541999999999",
        "respostas": {
            "flags": {"is_ttc": True, "bad_sperm": True},
            "temperatura": "quente",
            "score": 90,
            "historico": "Tentante há 1 ano, exames alterados."
        }
    })

    print("\n🔹 Etapa 3) Mensagem final do WhatsApp após Forms")
    await process_zapi_payload({
        "phone": "5541999999999",
        "senderName": "Carla",
        "message": "Pronto, já preenchi o formulário."
    })

if __name__ == "__main__":
    asyncio.run(main())
