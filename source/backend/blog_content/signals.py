# backend/blog_content/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from users_core.models import CustomUser
from .models import BlogAuthor

@receiver(post_save, sender=CustomUser)
def create_blog_author_for_user(sender, instance, created, **kwargs):
    """Crée automatiquement un BlogAuthor quand un CustomUser est créé"""
    if created and not hasattr(instance, 'blog_author'):
        BlogAuthor.objects.create(
            user=instance,
            display_name=instance.get_full_name() or instance.username,
            bio="",
            expertise_topics=[]
        )