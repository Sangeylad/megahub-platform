# /var/www/megahub/source/backend/django_app/settings/test.py

from .base import *

# TEST ENVIRONMENT
DEBUG = False

ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1']

# Database - SQLite en mémoire (ultra rapide)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'OPTIONS': {
            'timeout': 20,
        },
        'TEST': {
            'NAME': ':memory:',
        }
    },
    'shortener': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'OPTIONS': {
            'timeout': 20,
        },
        'TEST': {
            'NAME': ':memory:',
        }
    }
}

# Désactiver migrations pour vitesse
class DisableMigrations:
    def __contains__(self, item):
        return True
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Celery synchrone pour tests
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Email backend test
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Cache en mémoire pour tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Pas de logging en test
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
    },
}

print("🧪 Django TEST settings loaded")