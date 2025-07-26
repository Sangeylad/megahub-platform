# /var/www/megahub/source/backend/django_app/settings/development.py

from .base import *

# DEVELOPMENT ENVIRONMENT
DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'testserver',
]

# ✅ Development - runserver sert directement, pas de collectstatic nécessaire
print("🔧 Django DEVELOPMENT settings loaded")

# ✅ CORS FIX - Support HMR Vite port 3001 + Build port 3000
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:3001',    # ← AJOUT HMR VITE
    'http://127.0.0.1:3001',    # ← AJOUT HMR VITE
]

# Database - Docker local
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'mhdb24_dev'),
        'USER': os.environ.get('POSTGRES_USER', 'SuperAdminduTurfu'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'MHub2401!'),
        'HOST': os.environ.get('POSTGRES_HOST', 'postgres'),
        'PORT': '5432',
    },
    'shortener': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('SHORTENER_DB_NAME', 'shortener_dev'),
        'USER': os.environ.get('SHORTENER_DB_USER', 'shortener_user'),
        'PASSWORD': os.environ.get('SHORTENER_DB_PASSWORD', 'ShortUrl2025!'),
        'HOST': os.environ.get('SHORTENER_DB_HOST', 'postgres-shortener'),
        'PORT': '5432',
    }
}

# ✅ CORS Development - Support HMR + Build
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

# ✅ FIX CORS_ALLOW_HEADERS - Import correct selon standards MegaHub
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'X-Brand-ID',  # ← Header custom MegaHub
]

# ✅ CORS_ALLOWED_ORIGINS - MISE À JOUR avec port 3001 HMR
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',      # Build Vite (docker)
    'http://127.0.0.1:3000',      # Build Vite (local)
    'http://localhost:3001',      # ← HMR Vite (npm run dev)
    'http://127.0.0.1:3001',      # ← HMR Vite (local)
]

CORS_EXPOSE_HEADERS = [
    'Content-Disposition',
    'Content-Length', 
    'Content-Type',
    'X-Total-Count',
]

# Celery Development
CELERY_TASK_ALWAYS_EAGER = False  # True pour tests synchrones
CELERY_TASK_EAGER_PROPAGATES = True

print("🔧 Django DEVELOPMENT settings loaded")