# backend/blog_content/apps.py

from django.apps import AppConfig

class BlogContentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'blog_content'
    verbose_name = 'Blog Content'
    def ready(self):
        import blog_content.signals