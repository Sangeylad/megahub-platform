# /var/www/megahub/backend/crm_analytics_core/models/base_models.py
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from crm_entities_core.models import CRMBaseMixin

class AnalyticsBaseMixin(CRMBaseMixin):
    """Mixin de base pour tous les éléments analytics CRM"""
    
    # Période d'analyse
    date_from = models.DateField(
        help_text="Date de début de la période"
    )
    date_to = models.DateField(
        help_text="Date de fin de la période"
    )
    
    # Granularité
    GRANULARITY_CHOICES = [
        ('hourly', 'Horaire'),
        ('daily', 'Quotidien'),
        ('weekly', 'Hebdomadaire'),
        ('monthly', 'Mensuel'),
        ('quarterly', 'Trimestriel'),
        ('yearly', 'Annuel'),
    ]
    granularity = models.CharField(
        max_length=15,
        choices=GRANULARITY_CHOICES,
        default='daily',
        help_text="Granularité des données"
    )
    
    # Métadonnées
    last_calculated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Dernière mise à jour des calculs"
    )
    calculation_duration_ms = models.IntegerField(
        null=True,
        blank=True,
        help_text="Durée du calcul (millisecondes)"
    )
    
    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['date_from', 'date_to']),
            models.Index(fields=['granularity']),
            models.Index(fields=['last_calculated_at']),
        ]
