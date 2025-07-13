# /var/www/megahub/source/backend/django_app/settings/production.py

from .base import *

# PRODUCTION ENVIRONMENT
DEBUG = False

ALLOWED_HOSTS = [
    'backoffice.humari.fr', 
    'megahub.humari.fr', 
    'api.megahub.humari.fr',
]

CSRF_TRUSTED_ORIGINS = [
    'https://backoffice.humari.fr', 
    'https://megahub.humari.fr', 
    'https://api.megahub.humari.fr'
]

# ✅ Database - Production (OPTIONS corrigées)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'mhdb24'),
        'USER': os.environ.get('POSTGRES_USER', 'SuperAdminduTurfu'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'MHub2401!'),
        'HOST': os.environ.get('POSTGRES_HOST', 'postgres'),
        'PORT': '5432',
        'OPTIONS': {
            'connect_timeout': 10,
            # ✅ REMOVED: 'statement_timeout' - option invalide
        },
    },
    'shortener': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('SHORTENER_DB_NAME', 'shortener_db'),
        'USER': os.environ.get('SHORTENER_DB_USER', 'shortener_user'),
        'PASSWORD': os.environ.get('SHORTENER_DB_PASSWORD', 'ShortUrl2025!'),
        'HOST': os.environ.get('SHORTENER_DB_HOST', 'postgres-shortener'),
        'PORT': '5432',
        'OPTIONS': {
            'connect_timeout': 10,
        },
    }
}

# CORS Production
CORS_ORIGIN_ALLOW_ALL = False
CORS_ALLOW_CREDENTIALS = True

from corsheaders.defaults import default_headers
CORS_ALLOW_HEADERS = list(default_headers) + [
    'X-Brand-ID',
]

CORS_ALLOWED_ORIGINS = [
    'https://megahub.humari.fr',
    'https://backoffice.humari.fr',
    'https://api.megahub.humari.fr',
    'https://humari.fr',
    'https://www.humari.fr',
]

CORS_EXPOSE_HEADERS = [
    'Content-Disposition',
    'Content-Length', 
    'Content-Type',
    'X-Total-Count',
]

# ✅ Static files production optimisées
STATIC_ROOT = '/app/staticfiles'

# Storage avec compression et optimisations production
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# Pas de dossiers supplémentaires en prod
STATICFILES_DIRS = []

# Sécurité production STRICTE
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Rate limiting production
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'].update({
    'anon': '50/day',  # Plus strict qu'en dev
    'user': '5000/day',
})

print("🚀 Django PRODUCTION settings loaded")