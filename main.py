# main.py

from fastapi import FastAPI
from dotenv import load_dotenv
import os

# Carrega as variáveis de ambiente do .env usando caminho absoluto
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

from routers.zapi_webhook import router as zapi_router  # Import relativo como antes

# Instância principal do app
app = FastAPI(
    title="N.O.R.A. API",
    version="1.0.0",
    description="Inteligência Estratégica N.O.R.A. conectada ao WhatsApp via Z-API"
)

# Inclui rotas da Z-API
app.include_router(zapi_router)

# Health check
@app.get("/")
async def health_check():
    return {"status": "N.O.R.A. está ativa e saudável 🚀"}
