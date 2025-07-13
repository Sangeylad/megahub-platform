# backend/seo_pages_workflow/models/scheduling_models.py

from django.db import models
from django.utils import timezone

from .base_models import PageWorkflowBaseModel

class PageScheduling(PageWorkflowBaseModel):
    """Publication programmée des pages"""
    
    page = models.OneToOneField(
        'seo_pages_content.Page',
        on_delete=models.CASCADE,
        related_name='scheduling'
    )
    
    scheduled_publish_date = models.DateTimeField(
        null=True, blank=True,
        help_text="Date/heure de publication programmée"
    )
    
    scheduled_unpublish_date = models.DateTimeField(
        null=True, blank=True,
        help_text="Date/heure de dépublication programmée"
    )
    
    auto_publish = models.BooleanField(
        default=False,
        help_text="Publication automatique à la date programmée"
    )
    
    scheduled_by = models.ForeignKey(
        'users_core.CustomUser',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='scheduled_pages',
        help_text="Utilisateur ayant programmé la publication"
    )
    
    notes = models.TextField(
        blank=True,
        help_text="Notes sur la programmation"
    )
    
    def is_ready_to_publish(self):
        """Vérifie si la page est prête à être publiée"""
        if not self.scheduled_publish_date:
            return False
        return timezone.now() >= self.scheduled_publish_date
    
    def is_ready_to_unpublish(self):
        """Vérifie si la page doit être dépubliée"""
        if not self.scheduled_unpublish_date:
            return False
        return timezone.now() >= self.scheduled_unpublish_date
    
    def __str__(self):
        return f"Scheduling: {self.page.title}"
    
    class Meta:
        db_table = 'seo_pages_workflow_scheduling'
        ordering = ['scheduled_publish_date', '-created_at']  # 🔧 AJOUTER CETTE LIGNE
        verbose_name = "Programmation de Page"
        verbose_name_plural = "Programmations de Page"
        indexes = [
            models.Index(fields=['scheduled_publish_date', 'auto_publish']),
        ]