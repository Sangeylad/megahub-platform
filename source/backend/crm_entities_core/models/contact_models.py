# /var/www/megahub/backend/crm_entities_core/models/contact_models.py
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .base_models import CRMBaseMixin, GDPRMixin

class Contact(CRMBaseMixin, GDPRMixin):
    """Contact personne dans le CRM"""
    
    SALUTATIONS = [
        ('mr', 'Monsieur'),
        ('mrs', 'Madame'),
        ('miss', 'Mademoiselle'),
        ('dr', 'Docteur'),
        ('prof', 'Professeur'),
    ]
    
    LEAD_SOURCES = [
        ('website', 'Site Web'),
        ('social_media', 'Réseaux Sociaux'),
        ('referral', 'Recommandation'),
        ('cold_call', 'Appel à froid'),
        ('trade_show', 'Salon'),
        ('webinar', 'Webinaire'),
        ('content_marketing', 'Content Marketing'),
        ('paid_ads', 'Publicités Payantes'),
        ('partner', 'Partenaire'),
        ('other', 'Autre'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(
        'crm_entities_core.Account',
        on_delete=models.CASCADE,
        related_name='contacts',
        help_text="Compte associé"
    )
    
    # Informations personnelles
    salutation = models.CharField(
        max_length=10,
        choices=SALUTATIONS,
        blank=True,
        help_text="Civilité"
    )
    first_name = models.CharField(
        max_length=100,
        help_text="Prénom"
    )
    last_name = models.CharField(
        max_length=100,
        help_text="Nom de famille"
    )
    
    # Informations professionnelles
    job_title = models.CharField(
        max_length=100,
        blank=True,
        help_text="Poste/Fonction"
    )
    department = models.CharField(
        max_length=100,
        blank=True,
        help_text="Département"
    )
    
    # Contact
    email = models.EmailField(
        unique=True,
        help_text="Email principal"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Téléphone"
    )
    mobile = models.CharField(
        max_length=20,
        blank=True,
        help_text="Mobile"
    )
    linkedin_url = models.URLField(
        blank=True,
        help_text="Profil LinkedIn"
    )
    
    # Adresse (si différente du compte)
    mailing_street = models.CharField(max_length=255, blank=True)
    mailing_city = models.CharField(max_length=100, blank=True)
    mailing_state = models.CharField(max_length=100, blank=True)
    mailing_postal_code = models.CharField(max_length=20, blank=True)
    mailing_country = models.CharField(max_length=100, blank=True)
    
    # Origine et qualification
    lead_source = models.CharField(
        max_length=20,
        choices=LEAD_SOURCES,
        blank=True,
        help_text="Source du lead"
    )
    lead_source_detail = models.CharField(
        max_length=200,
        blank=True,
        help_text="Détail source du lead"
    )
    
    # Statut
    is_primary_contact = models.BooleanField(
        default=False,
        help_text="Contact principal du compte"
    )
    is_decision_maker = models.BooleanField(
        default=False,
        help_text="Décideur"
    )
    is_influencer = models.BooleanField(
        default=False,
        help_text="Influenceur dans les décisions"
    )
    
    # Scoring
    lead_score = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Score de qualification (0-100)"
    )
    engagement_score = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Score d'engagement (0-100)"
    )
    
    # Préférences communication
    email_opt_out = models.BooleanField(
        default=False,
        help_text="Opt-out email"
    )
    phone_opt_out = models.BooleanField(
        default=False,
        help_text="Opt-out téléphone"
    )
    preferred_contact_method = models.CharField(
        max_length=20,
        choices=[
            ('email', 'Email'),
            ('phone', 'Téléphone'),
            ('linkedin', 'LinkedIn'),
            ('no_contact', 'Aucun contact'),
        ],
        default='email',
        help_text="Méthode de contact préférée"
    )
    
    # Dates importantes
    last_activity_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Dernière activité"
    )
    last_email_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Dernier email"
    )
    last_call_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Dernier appel"
    )
    
    # Notes
    description = models.TextField(
        blank=True,
        help_text="Description/Notes sur le contact"
    )
    
    class Meta:
        db_table = 'crm_contact'
        ordering = ['last_name', 'first_name']
        verbose_name = 'Contact CRM'
        verbose_name_plural = 'Contacts CRM'
        indexes = [
            models.Index(fields=['brand', 'account']),
            models.Index(fields=['email']),
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['is_primary_contact']),
            models.Index(fields=['lead_score']),
            models.Index(fields=['is_decision_maker']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.account.name})"
    
    @property
    def full_name(self):
        """Nom complet du contact"""
        parts = []
        if self.salutation:
            parts.append(self.get_salutation_display())
        parts.extend([self.first_name, self.last_name])
        return ' '.join(parts)
    
    @property
    def display_name(self):
        """Nom d'affichage (prénom nom)"""
        return f"{self.first_name} {self.last_name}"
    
    def can_be_contacted(self, method='email'):
        """Vérifie si le contact peut être contacté par la méthode donnée"""
        if self.is_opted_out():
            return False
        
        if method == 'email' and self.email_opt_out:
            return False
        elif method == 'phone' and self.phone_opt_out:
            return False
        
        return True
    
    def get_full_address(self):
        """Retourne l'adresse complète formatée"""
        if not self.mailing_street:
            # Utiliser l'adresse du compte si pas d'adresse propre
            return self.account.get_full_address('billing')
        
        parts = [
            self.mailing_street,
            f"{self.mailing_postal_code} {self.mailing_city}",
            self.mailing_state,
            self.mailing_country
        ]
        return '\n'.join([part for part in parts if part.strip()])
