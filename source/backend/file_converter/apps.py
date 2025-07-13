# backend/file_converter/apps.py
from django.apps import AppConfig


class FileConverterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'file_converter'
