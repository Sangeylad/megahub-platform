# /var/www/megahub/backend/crm_entities_core/models/base_models.py
from django.db import models
from django.utils import timezone
from common.models.mixins import TimestampedMixin, SoftDeleteMixin

class CRMBaseMixin(TimestampedMixin, SoftDeleteMixin):
    """Mixin de base pour toutes les entités CRM"""
    
    brand = models.ForeignKey(
        'brands_core.Brand',
        on_delete=models.CASCADE,
        help_text="Brand gestionnaire de cette entité"
    )
    # ✅ FIX RELATED_NAME pour éviter clash avec CustomUser.email
    owner = models.ForeignKey(
        'users_core.CustomUser',
        on_delete=models.CASCADE,
        related_name='owned_%(class)s_entities',  # ✅ FIX Dynamic related_name
        help_text="Propriétaire/responsable de cette entité"
    )
    
    # Statut
    is_active = models.BooleanField(
        default=True,
        help_text="Entité active dans le CRM"
    )
    
    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['brand', 'is_active']),
            models.Index(fields=['owner']),
        ]

class GDPRMixin(models.Model):
    """Mixin GDPR pour entités avec données personnelles"""
    
    # Consentements
    consent_marketing = models.BooleanField(
        default=False,
        help_text="Consentement marketing"
    )
    consent_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date du consentement"
    )
    
    # Source et traçabilité
    data_source = models.CharField(
        max_length=100,
        blank=True,
        help_text="Source des données (import, formulaire, API)"
    )
    opt_out_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date d'opt-out"
    )
    
    # Anonymisation
    anonymized_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date d'anonymisation des données"
    )
    
    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['consent_marketing']),
            models.Index(fields=['opt_out_date']),
        ]
    
    def is_opted_out(self):
        """Vérifie si l'entité a opt-out"""
        return self.opt_out_date is not None
    
    def grant_marketing_consent(self):
        """Accorde le consentement marketing"""
        self.consent_marketing = True
        self.consent_date = timezone.now()
        self.opt_out_date = None
        self.save(update_fields=['consent_marketing', 'consent_date', 'opt_out_date'])
    
    def revoke_marketing_consent(self):
        """Révoque le consentement marketing"""
        self.consent_marketing = False
        self.opt_out_date = timezone.now()
        self.save(update_fields=['consent_marketing', 'opt_out_date'])
