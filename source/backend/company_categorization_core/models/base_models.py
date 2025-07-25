# /var/www/megahub/backend/company_categorization_core/models/base_models.py
from django.db import models
from common.models.mixins import TimestampedMixin, SoftDeleteMixin

class CategoryBaseMixin(TimestampedMixin, SoftDeleteMixin):
    """Mixin de base pour tous les profils de catégorisation d'entreprises"""
    
    company = models.OneToOneField(
        'company_core.Company',
        on_delete=models.CASCADE,
        help_text="Entreprise associée à ce profil"
    )
    
    # Données complémentaires communes
    additional_info = models.JSONField(
        default=dict,
        blank=True,
        help_text="Informations additionnelles spécifiques au secteur"
    )
    
    # Scoring secteur
    industry_score = models.IntegerField(
        null=True,
        blank=True,
        help_text="Score d'adéquation avec le secteur (0-100)"
    )
    
    # Validation
    is_validated = models.BooleanField(
        default=False,
        help_text="Profil validé par un expert secteur"
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
        help_text="Expert qui a validé le profil"
    )
    
    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['is_validated']),
            models.Index(fields=['industry_score']),
        ]
    
    def __str__(self):
        return f"{self.company.name} - {self.__class__.__name__}"
