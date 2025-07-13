# backend/seo_pages_workflow/models/history_models.py

from django.db import models
from django.utils import timezone

from .base_models import PageWorkflowBaseModel

class PageWorkflowHistory(PageWorkflowBaseModel):
    """Historique des changements de statut"""
    
    page = models.ForeignKey(
        'seo_pages_content.Page',
        on_delete=models.CASCADE,
        related_name='workflow_history'
    )
    
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    
    changed_by = models.ForeignKey(
        'users_core.CustomUser',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    
    notes = models.TextField(blank=True)
    
    def get_duration_display(self):
        """Retourne la durée depuis le changement sous forme lisible"""
        delta = timezone.now() - self.created_at
        
        if delta.days > 365:
            years = delta.days // 365
            return f"{years} an{'s' if years > 1 else ''}"
        elif delta.days > 30:
            months = delta.days // 30
            return f"{months} mois"
        elif delta.days > 0:
            return f"{delta.days} jour{'s' if delta.days > 1 else ''}"
        elif delta.seconds >= 3600:
            hours = delta.seconds // 3600
            return f"{hours} heure{'s' if hours > 1 else ''}"
        elif delta.seconds >= 60:
            minutes = delta.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''}"
        else:
            return "à l'instant"
    
    def __str__(self):
        return f"{self.page.title}: {self.old_status} → {self.new_status}"
    
    class Meta:
        db_table = 'seo_pages_workflow_history'
        ordering = ['-created_at']
        verbose_name = "Historique Workflow"
        verbose_name_plural = "Historiques Workflow"