# backend/seo_pages_seo/models/seo_models.py

from django.db import models

from .base_models import PageSeoBaseModel

class PageSEO(PageSeoBaseModel):
    """Métadonnées SEO et sitemap d'une page"""
    
    page = models.OneToOneField(
        'seo_pages_content.Page',
        on_delete=models.CASCADE,
        related_name='seo_config'
    )
    
    # SEO & Social
    featured_image = models.URLField(
        blank=True, null=True,
        help_text="Image principale pour réseaux sociaux"
    )
    
    # Sitemap
    sitemap_priority = models.DecimalField(
        max_digits=2, decimal_places=1,
        default=0.5,
        help_text="Priorité relative (0.0 à 1.0)"
    )
    
    CHANGEFREQ_CHOICES = [
        ('always', 'Always'),
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('never', 'Never')
    ]
    
    sitemap_changefreq = models.CharField(
        max_length=20,
        choices=CHANGEFREQ_CHOICES,
        default='weekly'
    )
    
    exclude_from_sitemap = models.BooleanField(
        default=False,
        help_text="Exclure de sitemap.xml"
    )
    
    def auto_assign_sitemap_defaults(self):
        """Auto-assign sitemap defaults par page type"""
        page_type_defaults = {
            'vitrine': {'priority': 0.8, 'changefreq': 'monthly'},
            'blog': {'priority': 0.6, 'changefreq': 'weekly'},
            'blog_category': {'priority': 0.7, 'changefreq': 'monthly'},
            'produit': {'priority': 0.9, 'changefreq': 'monthly'},
            'landing': {'priority': 1.0, 'changefreq': 'weekly'},
            'categorie': {'priority': 0.7, 'changefreq': 'monthly'},
            'legal': {'priority': 0.3, 'changefreq': 'yearly'},
            'outils': {'priority': 0.8, 'changefreq': 'weekly'},
            'autre': {'priority': 0.5, 'changefreq': 'weekly'},
        }
        
        defaults = page_type_defaults.get(self.page.page_type, {})
        if 'priority' in defaults:
            self.sitemap_priority = defaults['priority']
        if 'changefreq' in defaults:
            self.sitemap_changefreq = defaults['changefreq']
    
    def __str__(self):
        return f"SEO: {self.page.title}"
    
    class Meta:
        db_table = 'seo_pages_seo_seo'
        ordering = ['-updated_at']  # 🔧 AJOUTER CETTE LIGNE
        verbose_name = "Configuration SEO"
        verbose_name_plural = "Configurations SEO"
        indexes = [
            models.Index(fields=['page', 'sitemap_priority']),
        ]
