# utils/logger.py

from datetime import datetime
import json

def log_event(titulo: str, conteudo: dict):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n🔹 [{timestamp}] {titulo}")
    print(json.dumps(conteudo, indent=2, ensure_ascii=False))
