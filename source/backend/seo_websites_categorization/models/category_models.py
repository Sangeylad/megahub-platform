# backend/seo_websites_categorization/models/category_models.py

from django.db import models
from django.utils.text import slugify
import logging

from .base_models import SeoWebsitesCategorizationBaseModel

logger = logging.getLogger(__name__)

class WebsiteCategory(SeoWebsitesCategorizationBaseModel):
    """Catégorie de websites (E-commerce, Services, Santé, etc.)"""
    
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    color = models.CharField(
        max_length=7, 
        default='#6366f1',
        help_text="Couleur hexadécimale pour l'interface"
    )
    
    # Hiérarchie parent-enfant
    parent = models.ForeignKey(
        'self',
        null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='subcategories'
    )
    
    # Métriques SEO typiques pour cette catégorie
    typical_da_range_min = models.IntegerField(
        null=True, blank=True,
        help_text="DA minimum typique pour cette catégorie"
    )
    typical_da_range_max = models.IntegerField(
        null=True, blank=True,
        help_text="DA maximum typique pour cette catégorie"
    )
    typical_pages_count = models.IntegerField(
        null=True, blank=True,
        help_text="Nombre de pages typique"
    )
    
    # Ordre d'affichage
    display_order = models.PositiveIntegerField(default=0)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name
    
    def get_full_path(self):
        """Retourne le chemin complet de la catégorie"""
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.name}"
        return self.name
    
    def get_websites_count(self):
        """Nombre de websites dans cette catégorie"""
        return self.websites.count()
    
    def get_subcategories_count(self):
        """Nombre de sous-catégories"""
        return self.subcategories.count()
    
    def is_root_category(self):
        """Vérifie si c'est une catégorie racine"""
        return self.parent is None
    
    def get_level(self):
        """Retourne le niveau dans la hiérarchie (0 = racine)"""
        if self.parent is None:
            return 0
        return self.parent.get_level() + 1
    
    class Meta:
        db_table = 'seo_websites_categorization_category'
        ordering = ['display_order', 'name']
        verbose_name = "Catégorie de Website"
        verbose_name_plural = "Catégories de Websites"
        indexes = [
            models.Index(fields=['parent', 'display_order']),
            models.Index(fields=['slug']),
        ]

class WebsiteCategorization(SeoWebsitesCategorizationBaseModel):
    """Association Website ↔ Catégorie (Many-to-Many avec métadonnées)"""
    
    website = models.ForeignKey(
        'seo_websites_core.Website',
        on_delete=models.CASCADE,
        related_name='categorizations'
    )
    category = models.ForeignKey(
        WebsiteCategory,
        on_delete=models.CASCADE,
        related_name='websites'
    )
    
    # Métadonnées de catégorisation
    is_primary = models.BooleanField(
        default=False,
        help_text="Catégorie principale du website"
    )
    confidence_score = models.FloatField(
        null=True, blank=True,
        help_text="Score de confiance de la catégorisation (0.0-1.0)"
    )
    categorized_by = models.ForeignKey(
        'users_core.CustomUser',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        help_text="Utilisateur qui a fait la catégorisation"
    )
    
    # Source de la catégorisation
    CATEGORIZATION_SOURCE_CHOICES = [
        ('manual', 'Manuelle'),
        ('automatic', 'Automatique'),
        ('ai_suggested', 'Suggérée par IA'),
        ('imported', 'Importée'),
    ]
    source = models.CharField(
        max_length=20,
        choices=CATEGORIZATION_SOURCE_CHOICES,
        default='manual'
    )
    
    notes = models.TextField(
        blank=True,
        help_text="Notes sur cette catégorisation"
    )
    
    def __str__(self):
        primary_indicator = " (Primary)" if self.is_primary else ""
        return f"{self.website.name} → {self.category.name}{primary_indicator}"
    
    class Meta:
        db_table = 'seo_websites_categorization_association'
        unique_together = ['website', 'category']
        ordering = ['-is_primary', 'category__name']
        verbose_name = "Catégorisation de Website"
        verbose_name_plural = "Catégorisations de Websites"
        indexes = [
            models.Index(fields=['website', 'is_primary']),
            models.Index(fields=['category', 'is_primary']),
            models.Index(fields=['source']),
        ]