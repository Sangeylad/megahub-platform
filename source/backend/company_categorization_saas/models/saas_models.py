# /var/www/megahub/backend/company_categorization_saas/models/saas_models.py
from django.db import models
from company_categorization_core.models import CategoryBaseMixin

class SaasCompanyProfile(CategoryBaseMixin):
    """Profil spécialisé pour entreprises SaaS"""
    
    SAAS_VERTICALS = [
        ('crm', 'CRM & Sales'),
        ('marketing', 'Marketing Automation'),
        ('hr', 'RH & Talents'),
        ('accounting', 'Comptabilité & Finance'),
        ('project_mgmt', 'Gestion de Projets'),
        ('communication', 'Communication & Collaboration'),
        ('analytics', 'Analytics & BI'),
        ('ecommerce', 'E-commerce & Retail'),
        ('education', 'EdTech & Formation'),
        ('vertical_saas', 'SaaS Vertical Spécialisé'),
    ]
    
    TARGET_MARKETS = [
        ('b2b', 'B2B'),
        ('b2c', 'B2C'),
        ('b2b2c', 'B2B2C'),
        ('marketplace', 'Marketplace'),
    ]
    
    vertical = models.CharField(
        max_length=20,
        choices=SAAS_VERTICALS,
        help_text="Vertical SaaS principal"
    )
    target_market = models.CharField(
        max_length=15,
        choices=TARGET_MARKETS,
        default='b2b',
        help_text="Marché cible"
    )
    
    # Modèle business SaaS
    pricing_model = models.CharField(
        max_length=50,
        default='subscription',
        help_text="Modèle de pricing (subscription, usage-based, freemium)"
    )
    has_free_tier = models.BooleanField(
        default=False,
        help_text="Dispose d'une offre gratuite"
    )
    has_enterprise_tier = models.BooleanField(
        default=False,
        help_text="Dispose d'une offre Enterprise"
    )
    
    # Métriques SaaS
    mrr_estimate = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="MRR estimé (€)"
    )
    arr_estimate = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="ARR estimé (€)"
    )
    customer_count = models.IntegerField(
        null=True,
        blank=True,
        help_text="Nombre de clients"
    )
    churn_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Taux de churn mensuel (%)"
    )
    
    # Stack technique
    primary_tech_stack = models.CharField(
        max_length=100,
        blank=True,
        help_text="Stack technique principal (ex: React/Node.js, Django/Python)"
    )
    hosting_provider = models.CharField(
        max_length=50,
        blank=True,
        help_text="Fournisseur d'hébergement (AWS, GCP, Azure)"
    )
    
    # Intégrations
    api_integrations_count = models.IntegerField(
        null=True,
        blank=True,
        help_text="Nombre d'intégrations API disponibles"
    )
    has_public_api = models.BooleanField(
        default=False,
        help_text="Dispose d'une API publique"
    )
    
    class Meta:
        db_table = 'saas_company_profile'
        verbose_name = 'Profil SaaS'
        verbose_name_plural = 'Profils SaaS'
        indexes = [
            models.Index(fields=['vertical']),
            models.Index(fields=['target_market']),
            models.Index(fields=['has_enterprise_tier']),
        ]
    
    def get_business_model_summary(self):
        """Résumé du modèle business"""
        tiers = []
        if self.has_free_tier:
            tiers.append("Free")
        tiers.append("Paid")
        if self.has_enterprise_tier:
            tiers.append("Enterprise")
        
        return f"{self.get_target_market_display()} - {'/'.join(tiers)}"
