# backend/blog_editor/apps.py

from django.apps import AppConfig

class BlogEditorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog_editor'
    verbose_name = 'Blog Editor'