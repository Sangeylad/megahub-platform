# backend/seo_pages_layout/models/layout_models.py

from django.db import models

from .base_models import PageLayoutBaseModel

class PageLayout(PageLayoutBaseModel):
    """Configuration JSON pour le renderer Next.js"""
    
    page = models.OneToOneField(
        'seo_pages_content.Page',
        on_delete=models.CASCADE,
        related_name='layout_config'
    )
    
    RENDER_STRATEGY_CHOICES = [
        ('sections', 'Page Builder Sections'),
        ('markdown', 'Markdown Content'),
        ('custom', 'Custom Template'),
    ]
    
    render_strategy = models.CharField(
        max_length=20,
        choices=RENDER_STRATEGY_CHOICES,
        default='sections'
    )
    
    layout_data = models.JSONField(
        default=dict,
        help_text="Configuration JSON pour le renderer"
    )
    
    def __str__(self):
        return f"Layout: {self.page.title} ({self.render_strategy})"
    
    class Meta:
        db_table = 'seo_pages_layout_layout'
        ordering = ['-updated_at']  # 🔧 AJOUTER CETTE LIGNE
        verbose_name = "Configuration Layout"
        verbose_name_plural = "Configurations Layout"
        indexes = [
            models.Index(fields=['page', 'render_strategy']),
        ]

