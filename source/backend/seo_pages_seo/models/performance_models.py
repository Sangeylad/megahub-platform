# backend/seo_pages_seo/models/performance_models.py

from django.db import models

from .base_models import PageSeoBaseModel

class PagePerformance(PageSeoBaseModel):
    """Métriques de performance d'une page"""
    
    page = models.OneToOneField(
        'seo_pages_content.Page',
        on_delete=models.CASCADE,
        related_name='performance'
    )
    
    last_rendered_at = models.DateTimeField(
        null=True, blank=True,
        help_text="Dernière génération statique"
    )
    
    render_time_ms = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Temps de rendu en millisecondes"
    )
    
    cache_hits = models.PositiveIntegerField(
        default=0,
        help_text="Nombre de hits cache"
    )
    
    last_crawled_at = models.DateTimeField(
        null=True, blank=True,
        help_text="Dernière visite crawler Google"
    )
    
    def needs_regeneration(self):
        """Vérifie si la page doit être régénérée"""
        if not self.last_rendered_at:
            return True
        return self.page.updated_at > self.last_rendered_at
    
    def __str__(self):
        return f"Performance: {self.page.title}"
    
    class Meta:
        db_table = 'seo_pages_seo_performance'
        ordering = ['-updated_at']  # 🔧 AJOUTER CETTE LIGNE
        verbose_name = "Performance de Page"
        verbose_name_plural = "Performances de Page"
        indexes = [
            models.Index(fields=['page', 'last_rendered_at']),
        ]
