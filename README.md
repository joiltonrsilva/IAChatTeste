# NORAAI

## Preparação do ambiente

### Instalando o Ollama:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Instalando o modelo do Ollama:
```bash
ollama pull gemma:2b
```

### Criação do ambiente virtual
```bash
python3 -m venv .venv
```

### Ativação do ambiente virtual
```bash
source .venv/bin/activate
```

### Instalação das dependências
```bash
pip install -r requirements.txt
```
### Realizar a instalação do Docker
```bash
sudo apt update && sudo apt upgrade -y && sudo apt install docker.io -y && sudo systemctl start docker && sudo systemctl enable docker && sudo usermod -aG docker $USER
```

### Criando o container do Redis
```bash
docker run --name redis-test -p 6379:6379 redis:7-alpine
```

### Na página do Supabase, criar um projeto e copiar a chave de API


### Iniciar o servidor:
```bash
fastapi dev main.py
```



