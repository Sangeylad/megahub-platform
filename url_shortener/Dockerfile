FROM python:3.11-slim

# Sécurité : utilisateur non-root
RUN groupadd -r flask && useradd -r -g flask flask

# Dépendances système pour psycopg2
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Répertoire de travail
WORKDIR /app

# Installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier l'application
COPY . .

# Permissions sécurisées
RUN chown -R flask:flask /app
USER flask

# Port d'exposition
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python health.py

# Commande de démarrage (production avec Gunicorn)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "30", "--keep-alive", "2", "app:app"]