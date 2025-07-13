# backend/onboarding_trials/models/trial_event.py
from django.db import models
from django.utils import timezone

from common.models.mixins import TimestampedMixin

class TrialEvent(TimestampedMixin):
    """Events du trial pour tracking et analytics"""
    
    EVENT_TYPES = [
        ('trial_start', 'Trial démarré'),
        ('trial_warning_7', 'Avertissement 7 jours'),
        ('trial_warning_3', 'Avertissement 3 jours'),
        ('trial_warning_1', 'Avertissement 1 jour'),
        ('trial_expired', 'Trial expiré'),
        ('trial_extended', 'Trial étendu'),
        ('auto_upgrade', 'Upgrade automatique'),
        ('manual_upgrade', 'Upgrade manuel'),
        ('trial_converted', 'Trial converti'),
    ]
    
    # Relations
    company = models.ForeignKey(
        'company_core.Company',
        on_delete=models.CASCADE,
        related_name='trial_events',
        help_text="Company concernée"
    )
    
    # Event details
    event_type = models.CharField(
        max_length=30,
        choices=EVENT_TYPES,
        help_text="Type d'événement trial"
    )
    
    event_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Données JSON de l'événement"
    )
    
    # Metadata
    triggered_by = models.ForeignKey(
        'users_core.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User qui a déclenché l'événement"
    )
    
    processed = models.BooleanField(
        default=False,
        help_text="Événement traité"
    )
    
    class Meta:
        db_table = 'trial_event'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company', 'event_type']),
            models.Index(fields=['event_type', 'processed']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"[{self.get_event_type_display()}] {self.company.name}"
    
    def mark_as_processed(self):
        """Marque l'événement comme traité"""
        self.processed = True
        self.save(update_fields=['processed'])
    
    def get_event_summary(self):
        """Résumé pour API"""
        return {
            'id': self.id,
            'event_type': self.event_type,
            'event_type_display': self.get_event_type_display(),
            'event_data': self.event_data,
            'triggered_by': self.triggered_by.username if self.triggered_by else None,
            'processed': self.processed,
            'created_at': self.created_at
        }