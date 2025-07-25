# /var/www/megahub/backend/company_categorization_healthcare/models/healthcare_models.py
from django.db import models
from company_categorization_core.models import CategoryBaseMixin

class HealthcareCompanyProfile(CategoryBaseMixin):
    """Profil spécialisé pour entreprises de santé"""
    
    HEALTHCARE_TYPES = [
        ('clinic', 'Clinique & Cabinet Médical'),
        ('hospital', 'Hôpital & Centre Hospitalier'),
        ('pharmacy', 'Pharmacie & Parapharmacie'),
        ('laboratory', 'Laboratoire d\'Analyses'),
        ('medtech', 'MedTech & Dispositifs Médicaux'),
        ('healthtech', 'HealthTech & E-santé'),
        ('insurance', 'Assurance Santé'),
        ('wellness', 'Bien-être & Prévention'),
        ('research', 'Recherche Médicale'),
    ]
    
    SPECIALTIES = [
        ('general', 'Médecine Générale'),
        ('cardiology', 'Cardiologie'),
        ('dermatology', 'Dermatologie'),
        ('pediatrics', 'Pédiatrie'),
        ('gynecology', 'Gynécologie'),
        ('orthopedics', 'Orthopédie'),
        ('psychiatry', 'Psychiatrie'),
        ('oncology', 'Oncologie'),
        ('ophthalmology', 'Ophtalmologie'),
        ('dentistry', 'Dentaire'),
        ('multi_specialty', 'Multi-spécialités'),
    ]
    
    healthcare_type = models.CharField(
        max_length=20,
        choices=HEALTHCARE_TYPES,
        help_text="Type d'activité santé"
    )
    primary_specialty = models.CharField(
        max_length=20,
        choices=SPECIALTIES,
        default='general',
        help_text="Spécialité médicale principale"
    )
    
    # Autorisation et régulation
    health_license_number = models.CharField(
        max_length=50,
        blank=True,
        help_text="Numéro d'autorisation sanitaire"
    )
    accreditation_bodies = models.TextField(
        blank=True,
        help_text="Organismes d'accréditation (HAS, etc.)"
    )
    
    # Capacité et infrastructure
    bed_capacity = models.IntegerField(
        null=True,
        blank=True,
        help_text="Capacité d'accueil (lits/places)"
    )
    staff_count = models.IntegerField(
        null=True,
        blank=True,
        help_text="Nombre de personnel médical"
    )
    consultation_rooms = models.IntegerField(
        null=True,
        blank=True,
        help_text="Nombre de salles de consultation"
    )
    
    # Services proposés
    emergency_services = models.BooleanField(
        default=False,
        help_text="Services d'urgence disponibles"
    )
    telemedicine_services = models.BooleanField(
        default=False,
        help_text="Services de télémédecine"
    )
    home_care_services = models.BooleanField(
        default=False,
        help_text="Services de soins à domicile"
    )
    
    # Équipements spécialisés
    has_imaging_equipment = models.BooleanField(
        default=False,
        help_text="Équipements d'imagerie (IRM, Scanner)"
    )
    has_surgery_facilities = models.BooleanField(
        default=False,
        help_text="Bloc opératoire disponible"
    )
    
    # Digital Health
    uses_ehr_system = models.BooleanField(
        default=False,
        help_text="Utilise un système de dossier médical électronique"
    )
    ehr_provider = models.CharField(
        max_length=50,
        blank=True,
        help_text="Fournisseur du système de DME"
    )
    has_patient_portal = models.BooleanField(
        default=False,
        help_text="Dispose d'un portail patient"
    )
    
    # Métriques
    patients_per_month = models.IntegerField(
        null=True,
        blank=True,
        help_text="Nombre de patients par mois"
    )
    average_consultation_duration = models.IntegerField(
        null=True,
        blank=True,
        help_text="Durée moyenne consultation (minutes)"
    )
    
    class Meta:
        db_table = 'healthcare_company_profile'
        verbose_name = 'Profil Santé'
        verbose_name_plural = 'Profils Santé'
        indexes = [
            models.Index(fields=['healthcare_type']),
            models.Index(fields=['primary_specialty']),
            models.Index(fields=['telemedicine_services']),
        ]
    
    def get_service_capabilities(self):
        """Capacités et services disponibles"""
        services = []
        if self.emergency_services:
            services.append("Urgences")
        if self.telemedicine_services:
            services.append("Télémédecine")
        if self.home_care_services:
            services.append("Soins à domicile")
        if self.has_imaging_equipment:
            services.append("Imagerie")
        if self.has_surgery_facilities:
            services.append("Chirurgie")
        return services
