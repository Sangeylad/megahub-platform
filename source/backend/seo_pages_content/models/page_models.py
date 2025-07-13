# backend/seo_pages_content/models/page_models.py

from django.db import models
from django.utils.text import slugify

from .base_models import PageContentBaseModel

class Page(PageContentBaseModel):
    """Page d'un site web - Contenu éditorial uniquement"""
    
    title = models.CharField(max_length=255)
    url_path = models.CharField(max_length=500, blank=True)
    meta_description = models.TextField(blank=True, null=True)
    
    website = models.ForeignKey(
        'seo_websites_core.Website',
        on_delete=models.CASCADE,
        related_name='pages'
    )
    
    # Classification
    SEARCH_INTENT_CHOICES = [
        ('TOFU', 'Top of Funnel'),
        ('MOFU', 'Middle of Funnel'),
        ('BOFU', 'Bottom of Funnel'),
    ]
    search_intent = models.CharField(
        max_length=10,
        choices=SEARCH_INTENT_CHOICES,
        null=True, blank=True
    )
    
    PAGE_TYPE_CHOICES = [
        ('vitrine', 'Vitrine'),
        ('blog', 'Blog'),
        ('blog_category', 'Catégorie Blog'),
        ('produit', 'Produit/Service'),
        ('landing', 'Landing Page'),
        ('categorie', 'Page Catégorie'),
        ('legal', 'Page Légale'),
        ('outils', 'Outils'),
        ('autre', 'Autre'),
    ]
    page_type = models.CharField(
        max_length=20,
        choices=PAGE_TYPE_CHOICES,
        default='vitrine'
    )
    
    def save(self, *args, **kwargs):
        """Auto-génération URL si pas définie"""
        if not self.url_path:
            slug = slugify(self.title)
            self.url_path = f"/{slug}"
        
        if self.url_path and not self.url_path.startswith('/'):
            self.url_path = f"/{self.url_path}"
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.title} - {self.website.name}"
    
    class Meta:
        db_table = 'seo_pages_content_page'
        ordering = ['website', 'url_path','-created_at']
        unique_together = ('website', 'url_path')
        verbose_name = "Page"
        verbose_name_plural = "Pages"
        indexes = [
            models.Index(fields=['website', 'page_type']),
            models.Index(fields=['url_path']),
        ]
