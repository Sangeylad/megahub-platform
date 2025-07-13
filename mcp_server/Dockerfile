# mcp_server/Dockerfile
FROM python:3.11-slim

WORKDIR /mcp_server

# Dépendances
COPY requirements.txt .
RUN pip install -r requirements.txt

# Code
COPY . .

# Port pour l'API HTTP
EXPOSE 8001

# Démarrage
CMD ["python", "main.py"]