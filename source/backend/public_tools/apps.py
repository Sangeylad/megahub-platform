# backend/public_tools/apps.py
from django.apps import AppConfig


class PublicToolsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'public_tools'
