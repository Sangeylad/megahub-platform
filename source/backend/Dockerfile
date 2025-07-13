# /var/www/megahub/source/backend/Dockerfile

# ==========================================
# MegaHub Backend - Production Dockerfile Django Multi-Environment
# ==========================================

FROM python:3.11-slim AS base

# Variables metadata
LABEL maintainer="MegaHub Team <tech@megahub.fr>"
LABEL version="3.0.0"
LABEL description="MegaHub Backend - Django with multi-environment support"

# ==========================================
# DÉPENDANCES SYSTÈME pour conversions fichiers + performance
# ==========================================
RUN apt-get update && apt-get install -y \
  # LibreOffice complet pour conversions
  libreoffice \
  libreoffice-writer \
  libreoffice-calc \
  libreoffice-impress \
  libreoffice-common \
  fonts-liberation \
  fonts-dejavu-core \
  # Outils PDF et conversions
  poppler-utils \
  pandoc \
  # Outils système
  curl \
  wget \
  git \
  # Build tools pour packages Python
  build-essential \
  pkg-config \
  # PostgreSQL client
  postgresql-client \
  # Nettoyage
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# ==========================================
# UTILISATEUR SÉCURISÉ
# ==========================================
RUN addgroup --gid 1004 megahub_devs && \
  adduser --disabled-password --gecos "" --uid 1000 --ingroup megahub_devs debian

WORKDIR /app

# ==========================================
# INSTALLATION DÉPENDANCES PYTHON
# ==========================================
# Copier requirements en premier pour optimiser cache Docker
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# ==========================================
# COPIE CODE SOURCE
# ==========================================
COPY . .

# ==========================================
# CONFIGURATION STOCKAGE & PERMISSIONS
# ==========================================
RUN mkdir -p \
  /app/logs \
  /app/storage/file_conversions/inputs \
  /app/storage/file_conversions/outputs \
  /app/storage/openai_exports \
  /app/storage/public_conversions \
  && chown -R debian:megahub_devs /app

# ==========================================
# SCRIPTS UTILITAIRES
# ==========================================
# Script de santé Django
COPY <<EOF /app/health_check.py
#!/usr/bin/env python3
import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_app.settings.production')
django.setup()

try:
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute("SELECT 1")
    print("✅ Database connection OK")
    sys.exit(0)
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    sys.exit(1)
EOF

RUN chmod +x /app/health_check.py

# ==========================================
# CHANGEMENT UTILISATEUR SÉCURISÉ
# ==========================================
USER debian

# ==========================================
# CONFIGURATION RUNTIME
# ==========================================
EXPOSE 8000

# Variables d'environnement par défaut
ENV PYTHONPATH=/app
ENV DJANGO_SETTINGS_MODULE=django_app.settings.production
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD python /app/health_check.py || exit 1

# Commande par défaut (peut être surchargée)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]