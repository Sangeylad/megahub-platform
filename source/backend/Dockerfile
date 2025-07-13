# /var/www/megahub/source/backend/Dockerfile
# ==========================================
# MegaHub Backend - Production Dockerfile Django Multi-Environment
# ✅ VERSION CORRIGÉE - Staticfiles Permissions Fix
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
# ✅ CONFIGURATION STOCKAGE & PERMISSIONS - STATICFILES FIX
# ==========================================
RUN mkdir -p \
  /app/logs \
  /app/storage/file_conversions/inputs \
  /app/storage/file_conversions/outputs \
  /app/storage/openai_exports \
  /app/storage/public_conversions \
  /app/staticfiles \
  && chown -R debian:megahub_devs /app

# ✅ CRÉATION STATICFILES avec permissions debian
RUN mkdir -p /app/staticfiles && \
  chown -R debian:megahub_devs /app/staticfiles && \
  chmod -R 755 /app/staticfiles

# ==========================================
# SCRIPTS UTILITAIRES
# ==========================================
# Script de santé Django avec syntaxe Docker correcte
RUN echo '#!/usr/bin/env python3' > /app/health_check.py && \
  echo 'import os' >> /app/health_check.py && \
  echo 'import sys' >> /app/health_check.py && \
  echo 'import django' >> /app/health_check.py && \
  echo 'from django.conf import settings' >> /app/health_check.py && \
  echo 'from django.core.management import execute_from_command_line' >> /app/health_check.py && \
  echo '' >> /app/health_check.py && \
  echo 'os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_app.settings.production")' >> /app/health_check.py && \
  echo 'django.setup()' >> /app/health_check.py && \
  echo '' >> /app/health_check.py && \
  echo 'try:' >> /app/health_check.py && \
  echo '    from django.db import connection' >> /app/health_check.py && \
  echo '    cursor = connection.cursor()' >> /app/health_check.py && \
  echo '    cursor.execute("SELECT 1")' >> /app/health_check.py && \
  echo '    print("✅ Database connection OK")' >> /app/health_check.py && \
  echo '    sys.exit(0)' >> /app/health_check.py && \
  echo 'except Exception as e:' >> /app/health_check.py && \
  echo '    print(f"❌ Database connection failed: {e}")' >> /app/health_check.py && \
  echo '    sys.exit(1)' >> /app/health_check.py && \
  chmod +x /app/health_check.py

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