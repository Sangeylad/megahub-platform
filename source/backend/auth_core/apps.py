# backend/auth_core/apps.py
from django.apps import AppConfig

class AuthCoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auth_core'
    verbose_name = 'Authentication Core'
    
    def ready(self):
        # Import signals si nécessaire
        pass
