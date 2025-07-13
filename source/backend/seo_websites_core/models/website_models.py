# backend/seo_websites_core/models/website_models.py

from django.db import models
import logging

from .base_models import WebsiteCoreBaseModel

logger = logging.getLogger(__name__)

class Website(WebsiteCoreBaseModel):
    """Site web associé à une marque - Core data uniquement"""
    
    name = models.CharField(max_length=255)
    url = models.URLField()
    
    # Relation 1:1 avec Brand
    brand = models.OneToOneField(
        'brands_core.Brand',
        on_delete=models.CASCADE,
        related_name='seo_website'
    )
    
    # Métriques SEO
    domain_authority = models.IntegerField(
        null=True, blank=True,
        help_text="Autorité de domaine de notre site"
    )
    max_competitor_backlinks = models.IntegerField(
        null=True, blank=True,
        help_text="Nombre maximal de backlinks de la concurrence"
    )
    max_competitor_kd = models.FloatField(
        null=True, blank=True,
        help_text="Difficulté keyword maximale des concurrents"
    )
    
    def __str__(self):
        return f"{self.name} ({self.brand.name})"
    
    def get_pages_count(self):
        """Nombre total de pages"""
        from seo_pages_content.models import Page
        return Page.objects.filter(website=self).count()
    
    class Meta:
        db_table = 'seo_websites_core_website'
        ordering = ['name']
        verbose_name = "Site Web"
        verbose_name_plural = "Sites Web"
        indexes = [
            models.Index(fields=['brand']),
        ]