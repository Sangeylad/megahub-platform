# /var/www/megahub/backend/company_categorization_realestate/models/realestate_models.py
from django.db import models
from company_categorization_core.models import CategoryBaseMixin

class RealEstateCompanyProfile(CategoryBaseMixin):
    """Profil spécialisé pour entreprises immobilières"""
    
    REALESTATE_TYPES = [
        ('agency', 'Agence Immobilière'),
        ('developer', 'Promoteur Immobilier'),
        ('property_mgmt', 'Gestion Locative'),
        ('investment', 'Investissement Immobilier'),
        ('construction', 'Construction & BTP'),
        ('proptech', 'PropTech & Innovation'),
        ('consulting', 'Conseil Immobilier'),
        ('commercial', 'Immobilier Commercial'),
        ('luxury', 'Immobilier de Luxe'),
    ]
    
    ACTIVITY_FOCUS = [
        ('residential', 'Résidentiel'),
        ('commercial', 'Commercial'),
        ('industrial', 'Industriel'),
        ('mixed', 'Mixte'),
        ('luxury', 'Luxe'),
        ('new_build', 'Neuf'),
        ('renovation', 'Rénovation'),
    ]
    
    business_type = models.CharField(
        max_length=20,
        choices=REALESTATE_TYPES,
        help_text="Type d'activité immobilière"
    )
    activity_focus = models.CharField(
        max_length=15,
        choices=ACTIVITY_FOCUS,
        help_text="Focus d'activité principal"
    )
    
    # Géographie
    primary_market = models.CharField(
        max_length=100,
        help_text="Marché géographique principal"
    )
    coverage_area = models.TextField(
        blank=True,
        help_text="Zone de couverture géographique"
    )
    
    # Métriques immobilières
    properties_under_management = models.IntegerField(
        null=True,
        blank=True,
        help_text="Nombre de biens en gestion"
    )
    average_property_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Valeur moyenne des biens (€)"
    )
    transactions_per_year = models.IntegerField(
        null=True,
        blank=True,
        help_text="Nombre de transactions annuelles"
    )
    
    # Spécialisations
    luxury_specialist = models.BooleanField(
        default=False,
        help_text="Spécialisé dans le luxe"
    )
    first_time_buyers_focus = models.BooleanField(
        default=False,
        help_text="Focus primo-accédants"
    )
    investment_focus = models.BooleanField(
        default=False,
        help_text="Focus investissement locatif"
    )
    
    # Certifications
    certifications = models.TextField(
        blank=True,
        help_text="Certifications professionnelles (FNAIM, etc.)"
    )
    insurance_coverage = models.CharField(
        max_length=100,
        blank=True,
        help_text="Assurance responsabilité civile professionnelle"
    )
    
    # PropTech
    uses_virtual_tours = models.BooleanField(
        default=False,
        help_text="Utilise la visite virtuelle"
    )
    has_mobile_app = models.BooleanField(
        default=False,
        help_text="Dispose d'une app mobile"
    )
    crm_system = models.CharField(
        max_length=50,
        blank=True,
        help_text="Système CRM utilisé"
    )
    
    class Meta:
        db_table = 'realestate_company_profile'
        verbose_name = 'Profil Immobilier'
        verbose_name_plural = 'Profils Immobiliers'
        indexes = [
            models.Index(fields=['business_type']),
            models.Index(fields=['activity_focus']),
            models.Index(fields=['luxury_specialist']),
        ]
    
    def get_specialization_tags(self):
        """Liste des spécialisations"""
        tags = []
        if self.luxury_specialist:
            tags.append("Luxe")
        if self.first_time_buyers_focus:
            tags.append("Primo-accédants")
        if self.investment_focus:
            tags.append("Investissement")
        if self.uses_virtual_tours:
            tags.append("Visite Virtuelle")
        if self.has_mobile_app:
            tags.append("App Mobile")
        return tags
