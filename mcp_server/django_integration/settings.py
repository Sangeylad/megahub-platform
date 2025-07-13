# mcp_server/django_integration/settings.py
"""
Settings Django ultra-minimal pour MCP
Seulement ce qui est nécessaire pour accéder aux modèles
"""
import os
from pathlib import Path

# Chemins
BASE_DIR = Path(__file__).resolve().parent.parent.parent / 'backend'

# Sécurité (pas critique pour MCP)
SECRET_KEY = 'mcp-server-local-key-not-for-production'
DEBUG = False
ALLOWED_HOSTS = ['*']

# Apps minimales (seulement nos modèles)
INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'business',
    'seo_analyzer',
]

# Middleware minimal
MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
]

# Base de données (même que backend)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'mhdb24'),
        'USER': os.getenv('POSTGRES_USER', 'SuperAdminduTurfu'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'MHub2401!'),
        'HOST': os.getenv('POSTGRES_HOST', 'postgres'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}

# Internationalisation
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_TZ = True

# Clé primaire par défaut
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Logging optimisé pour MCP
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '[MCP] {levelname} {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django.db.backends': {
            'level': 'WARNING',  # Pas de debug SQL
            'handlers': ['console'],
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# Pas de session, cache, files, etc.
USE_L10N = True