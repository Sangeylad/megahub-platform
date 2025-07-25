# /var/www/megahub/backend/crm_activities_core/models/base_models.py
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from crm_entities_core.models import CRMBaseMixin

class ActivityBaseMixin(CRMBaseMixin):
    """Mixin de base pour toutes les activités CRM"""
    
    # Relations génériques vers les entités CRM
    related_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        help_text="Type d'entité liée (Account, Contact, Opportunity)"
    )
    related_object_id = models.UUIDField(
        help_text="ID de l'entité liée"
    )
    related_object = GenericForeignKey('related_content_type', 'related_object_id')
    
    # Assignation - ✅ FIX RELATED_NAME pour éviter clash avec Email
    assigned_to = models.ForeignKey(
        'users_core.CustomUser',
        on_delete=models.CASCADE,
        related_name='assigned_activities_%(class)s',  # ✅ FIX Dynamic related_name
        help_text="Utilisateur assigné à cette activité"
    )
    
    # Dates
    scheduled_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date programmée"
    )
    completed_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date de completion"
    )
    due_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date d'échéance"
    )
    
    # Statut
    is_completed = models.BooleanField(
        default=False,
        help_text="Activité terminée"
    )
    is_high_priority = models.BooleanField(
        default=False,
        help_text="Priorité élevée"
    )
    
    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['related_content_type', 'related_object_id']),
            models.Index(fields=['assigned_to', 'is_completed']),
            models.Index(fields=['scheduled_date']),
            models.Index(fields=['due_date']),
        ]
    
    def __str__(self):
        return f"{self.__class__.__name__} - {self.assigned_to.get_full_name()}"
    
    @property
    def is_overdue(self):
        """Vérifie si l'activité est en retard"""
        from django.utils import timezone
        return (
            not self.is_completed and 
            self.due_date and 
            self.due_date < timezone.now()
        )
    
    def mark_as_completed(self):
        """Marque l'activité comme terminée"""
        from django.utils import timezone
        self.is_completed = True
        self.completed_date = timezone.now()
        self.save(update_fields=['is_completed', 'completed_date'])
