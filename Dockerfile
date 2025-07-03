# Etapa 1: Base da imagem
FROM python:3.11-slim

# Etapa 2: Setar diretório de trabalho
WORKDIR /app

# Etapa 3: Instalar dependências do sistema (opcional, mas útil para alguns pacotes Python)
RUN apt-get update && apt-get install -y build-essential && apt-get clean

# Etapa 4: Copiar arquivos do projeto
COPY . .

# Etapa 5: Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Etapa 6: Expor porta padrão FastAPI
EXPOSE 8000

# Etapa 7: Rodar a aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
