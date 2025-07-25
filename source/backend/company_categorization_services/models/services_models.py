# /var/www/megahub/backend/company_categorization_services/models/services_models.py
from django.db import models
from company_categorization_core.models import CategoryBaseMixin

class ServicesCompanyProfile(CategoryBaseMixin):
    """Profil spécialisé pour entreprises de services professionnels"""
    
    SERVICE_TYPES = [
        ('consulting', 'Conseil & Stratégie'),
        ('legal', 'Services Juridiques'),
        ('accounting', 'Comptabilité & Audit'),
        ('marketing', 'Marketing & Communication'),
        ('it_services', 'Services IT & Digital'),
        ('hr_services', 'RH & Recrutement'),
        ('training', 'Formation & Développement'),
        ('design', 'Design & Créatif'),
        ('architecture', 'Architecture & Ingénierie'),
        ('maintenance', 'Maintenance & Support'),
        ('logistics', 'Logistique & Transport'),
        ('security', 'Sécurité & Surveillance'),
    ]
    
    DELIVERY_MODELS = [
        ('on_premise', 'Sur Site Client'),
        ('remote', 'À Distance'),
        ('hybrid', 'Hybride'),
        ('office_based', 'En Agence'),
    ]
    
    service_type = models.CharField(
        max_length=20,
        choices=SERVICE_TYPES,
        help_text="Type de service principal"
    )
    delivery_model = models.CharField(
        max_length=15,
        choices=DELIVERY_MODELS,
        help_text="Modèle de prestation"
    )
    
    # Spécialisations
    specialization = models.CharField(
        max_length=100,
        blank=True,
        help_text="Spécialisation ou niche"
    )
    target_industries = models.TextField(
        blank=True,
        help_text="Secteurs clients cibles"
    )
    
    # Structure et équipe
    consultants_count = models.IntegerField(
        null=True,
        blank=True,
        help_text="Nombre de consultants/experts"
    )
    partners_count = models.IntegerField(
        null=True,
        blank=True,
        help_text="Nombre d'associés"
    )
    
    # Certifications professionnelles
    professional_certifications = models.TextField(
        blank=True,
        help_text="Certifications professionnelles (ISO, PMP, etc.)"
    )
    industry_memberships = models.TextField(
        blank=True,
        help_text="Adhésions organisations professionnelles"
    )
    
    # Métriques business
    hourly_rate_range = models.CharField(
        max_length=50,
        blank=True,
        help_text="Fourchette tarif horaire (€)"
    )
    project_size_range = models.CharField(
        max_length=50,
        blank=True,
        help_text="Fourchette taille projets (€)"
    )
    client_retention_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Taux de rétention clients (%)"
    )
    
    # Type de clients
    serves_sme = models.BooleanField(
        default=True,
        help_text="Sert les PME"
    )
    serves_large_corps = models.BooleanField(
        default=False,
        help_text="Sert les grandes entreprises"
    )
    serves_public_sector = models.BooleanField(
        default=False,
        help_text="Sert le secteur public"
    )
    
    # Méthodologies
    methodologies_used = models.TextField(
        blank=True,
        help_text="Méthodologies utilisées (Agile, Lean, Six Sigma)"
    )
    
    # Digital capabilities
    uses_project_mgmt_tools = models.BooleanField(
        default=False,
        help_text="Utilise des outils de gestion de projets"
    )
    offers_digital_deliverables = models.BooleanField(
        default=False,
        help_text="Livre des résultats digitaux"
    )
    has_proprietary_tools = models.BooleanField(
        default=False,
        help_text="Dispose d'outils propriétaires"
    )
    
    # Références
    notable_clients = models.TextField(
        blank=True,
        help_text="Clients notables (si public)"
    )
    case_studies_count = models.IntegerField(
        null=True,
        blank=True,
        help_text="Nombre d'études de cas documentées"
    )
    
    class Meta:
        db_table = 'services_company_profile'
        verbose_name = 'Profil Services'
        verbose_name_plural = 'Profils Services'
        indexes = [
            models.Index(fields=['service_type']),
            models.Index(fields=['delivery_model']),
            models.Index(fields=['serves_large_corps']),
        ]
    
    def get_client_segments(self):
        """Segments clients servis"""
        segments = []
        if self.serves_sme:
            segments.append("PME")
        if self.serves_large_corps:
            segments.append("Grandes Entreprises")
        if self.serves_public_sector:
            segments.append("Secteur Public")
        return segments or ["Non spécifié"]
    
    def get_capabilities_summary(self):
        """Résumé des capacités"""
        capabilities = []
        if self.uses_project_mgmt_tools:
            capabilities.append("Gestion Projet")
        if self.offers_digital_deliverables:
            capabilities.append("Livrables Digitaux")
        if self.has_proprietary_tools:
            capabilities.append("Outils Propriétaires")
        return capabilities
