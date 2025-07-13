# backend/blog_config/apps.py

from django.apps import AppConfig

class BlogConfigConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog_config'
    verbose_name = 'Blog Configuration'