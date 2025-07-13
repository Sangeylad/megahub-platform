# backend/blog_collections/apps.py

from django.apps import AppConfig

class BlogCollectionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog_collections'
    verbose_name = 'Blog Collections'