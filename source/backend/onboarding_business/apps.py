# backend/onboarding_business/apps.py

from django.apps import AppConfig


class OnboardingBusinessConfig(AppConfig):
    """Configuration app onboarding business - Setup explicite des business"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'onboarding_business'
    verbose_name = 'Onboarding Business'
    
    def ready(self):
        """Initialisation app - pas de signals ici"""
        pass