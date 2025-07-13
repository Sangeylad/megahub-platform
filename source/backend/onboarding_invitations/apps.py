# backend/onboarding_invitations/apps.py
from django.apps import AppConfig

class OnboardingInvitationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'onboarding_invitations'
    verbose_name = 'Onboarding Invitations'