# backend/file_compressor/apps.py
from django.apps import AppConfig


class FileCompressorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'file_compressor'
