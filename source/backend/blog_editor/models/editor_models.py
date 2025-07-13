# backend/blog_editor/models/editor_models.py

from django.db import models
from common.models.mixins import TimestampedMixin


class BlogContent(TimestampedMixin):
    """Contenu TipTap pour articles - séparé du core"""
    article = models.OneToOneField(
        'blog_content.BlogArticle',
        on_delete=models.CASCADE,
        related_name='content'
    )
    
    # Contenu TipTap complet
    content_tiptap = models.JSONField(
        null=True,
        blank=True,
        help_text="Contenu TipTap JSON complet"
    )
    content_html = models.TextField(
        blank=True,
        help_text="Version HTML rendue depuis TipTap"
    )
    content_text = models.TextField(
        blank=True,
        help_text="Version texte pour recherche"
    )
    
    # Version tracking
    version = models.PositiveIntegerField(default=1)
    last_edited_by = models.ForeignKey(
        'users_core.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    def __str__(self):
        return f"Contenu pour {self.article.page.title}"
    
    class Meta:
        verbose_name = "Contenu Blog"
        verbose_name_plural = "Contenus Blog"
        db_table = 'blog_editor_blogcontent'