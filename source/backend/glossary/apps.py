# backend/glossary/apps.py
from django.apps import AppConfig


class GlossaryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'glossary'
    verbose_name = 'Glossaire Business'