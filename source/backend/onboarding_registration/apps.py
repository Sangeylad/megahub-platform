# backend/onboarding_registration/apps.py
from django.apps import AppConfig

class OnboardingRegistrationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'onboarding_registration'
    verbose_name = 'Onboarding Registration'
    
    def ready(self):
        # 🔧 MIGRATION EXPLICITE : Signal désactivé
        # Architecture REST pure : User creation séparée du business setup
        # Front-end appelle explicitement /onboarding/business/setup/
        # import onboarding_registration.signals
        pass