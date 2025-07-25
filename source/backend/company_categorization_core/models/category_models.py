# /var/www/megahub/backend/company_categorization_core/models/category_models.py
from django.db import models
from common.models.mixins import TimestampedMixin, SoftDeleteMixin

class IndustryCategory(TimestampedMixin, SoftDeleteMixin):
    """Catégories d'industrie principales"""
    
    CATEGORY_TYPES = [
        ('fintech', 'Services Financiers & FinTech'),
        ('saas', 'Software as a Service'),
        ('realestate', 'Immobilier & Construction'),
        ('healthcare', 'Santé & Bien-être'),
        ('ecommerce', 'E-commerce & Retail'),
        ('services', 'Services Professionnels'),
        ('manufacturing', 'Industrie & Manufacturing'),
        ('education', 'Éducation & Formation'),
        ('media', 'Média & Communication'),
        ('hospitality', 'Hôtellerie & Tourisme'),
    ]
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Nom de la catégorie d'industrie"
    )
    category_type = models.CharField(
        max_length=20,
        choices=CATEGORY_TYPES,
        help_text="Type de catégorie"
    )
    description = models.TextField(
        help_text="Description détaillée de la catégorie"
    )
    
    # Hiérarchie
    parent_category = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories',
        help_text="Catégorie parent"
    )
    level = models.IntegerField(
        default=1,
        help_text="Niveau hiérarchique (1=principal, 2=sous-catégorie)"
    )
    
    # Métadonnées
    color_code = models.CharField(
        max_length=7,
        default='#6a5acd',
        help_text="Code couleur hex pour l'affichage"
    )
    icon_name = models.CharField(
        max_length=50,
        default='building',
        help_text="Nom de l'icône (Font Awesome)"
    )
    sort_order = models.IntegerField(
        default=0,
        help_text="Ordre d'affichage"
    )
    
    # Configuration
    is_active = models.BooleanField(
        default=True,
        help_text="Catégorie active"
    )
    requires_validation = models.BooleanField(
        default=False,
        help_text="Nécessite validation expert pour cette catégorie"
    )
    
    class Meta:
        db_table = 'industry_category'
        ordering = ['sort_order', 'name']
        verbose_name = 'Catégorie Industrie'
        verbose_name_plural = 'Catégories Industries'
        indexes = [
            models.Index(fields=['category_type']),
            models.Index(fields=['is_active']),
            models.Index(fields=['parent_category', 'level']),
        ]
    
    def __str__(self):
        return self.name

class CompanyCategory(TimestampedMixin, SoftDeleteMixin):
    """Association Company <-> Catégorie avec métadonnées"""
    
    company = models.ForeignKey(
        'company_core.Company',
        on_delete=models.CASCADE,
        related_name='company_categories',
        help_text="Entreprise catégorisée"
    )
    category = models.ForeignKey(
        IndustryCategory,
        on_delete=models.CASCADE,
        related_name='companies',
        help_text="Catégorie assignée"
    )
    
    # Métadonnées assignment
    is_primary = models.BooleanField(
        default=False,
        help_text="Catégorie principale de l'entreprise"
    )
    confidence_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Score de confiance de la catégorisation (0.00-100.00)"
    )
    
    # Source de la catégorisation
    SOURCE_CHOICES = [
        ('manual', 'Attribution Manuelle'),
        ('onboarding', 'Onboarding Utilisateur'),
        ('ai_detection', 'Détection IA'),
        ('api_enrichment', 'Enrichissement API'),
        ('admin_override', 'Override Admin'),
    ]
    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default='manual',
        help_text="Source de la catégorisation"
    )
    
    # Validation
    is_validated = models.BooleanField(
        default=False,
        help_text="Catégorisation validée"
    )
    validated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date de validation"
    )
    validated_by = models.ForeignKey(
        'users_core.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Utilisateur qui a validé"
    )
    
    class Meta:
        db_table = 'company_category'
        unique_together = ['company', 'category']
        ordering = ['-is_primary', '-confidence_score']
        verbose_name = 'Catégorie Entreprise'
        verbose_name_plural = 'Catégories Entreprises'
        indexes = [
            models.Index(fields=['company', 'is_primary']),
            models.Index(fields=['category', 'is_validated']),
            models.Index(fields=['source']),
        ]
    
    def __str__(self):
        primary_indicator = " (Principal)" if self.is_primary else ""
        return f"{self.company.name} - {self.category.name}{primary_indicator}"
