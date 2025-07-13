# /var/www/megahub/source/backend/django_app/settings/staging.py

from .base import *

# STAGING ENVIRONMENT
DEBUG = False

ALLOWED_HOSTS = [
    'staging.megahub.humari.fr',
    'staging-api.megahub.humari.fr',
    'backoffice.humari.fr',  # API partagée avec prod
    'localhost',
    'testserver',
]

CSRF_TRUSTED_ORIGINS = [
    'https://staging.megahub.humari.fr',
    'https://staging-api.megahub.humari.fr', 
    'https://backoffice.humari.fr',
]

# ✅ Database - Staging (OPTIONS corrigées)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'mhdb24_staging'),
        'USER': os.environ.get('POSTGRES_USER', 'SuperAdminduTurfu'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'MHub2401!'),
        'HOST': os.environ.get('POSTGRES_HOST', 'postgres'),
        'PORT': '5432',
        'OPTIONS': {
            'connect_timeout': 10,
            # ✅ REMOVED: options PostgreSQL invalides
        },
    },
    'shortener': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('SHORTENER_DB_NAME', 'shortener_staging'),
        'USER': os.environ.get('SHORTENER_DB_USER', 'shortener_user'),
        'PASSWORD': os.environ.get('SHORTENER_DB_PASSWORD', 'ShortUrl2025!'),
        'HOST': os.environ.get('SHORTENER_DB_HOST', 'postgres-shortener'),
        'PORT': '5432',
        'OPTIONS': {
            'connect_timeout': 10,
        },
    }
}

# CORS Staging
CORS_ORIGIN_ALLOW_ALL = False
CORS_ALLOW_CREDENTIALS = True

from corsheaders.defaults import default_headers
CORS_ALLOW_HEADERS = list(default_headers) + [
    'X-Brand-ID',
]

CORS_ALLOWED_ORIGINS = [
    'https://staging.megahub.humari.fr',
    'https://staging-api.megahub.humari.fr',
    'https://backoffice.humari.fr',
]

CORS_EXPOSE_HEADERS = [
    'Content-Disposition',
    'Content-Length', 
    'Content-Type',
    'X-Total-Count',
]

# ✅ Static files staging
STATIC_ROOT = '/app/staticfiles'

# Debug collectstatic en staging
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Sécurité staging (moins stricte que prod)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

print("🧪 Django STAGING settings loaded")