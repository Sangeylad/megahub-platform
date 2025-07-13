# backend/seo_pages_workflow/models/status_models.py

from django.db import models
from django.utils import timezone
import logging

from .base_models import PageWorkflowBaseModel

logger = logging.getLogger(__name__)

class PageStatus(PageWorkflowBaseModel):
    """Statut workflow d'une page"""
    
    page = models.OneToOneField(
        'seo_pages_content.Page',
        on_delete=models.CASCADE,
        related_name='workflow_status'
    )
    
    PAGE_STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('in_progress', 'En développement'),
        ('pending_review', 'En attente de review'),
        ('under_review', 'En cours de review'),
        ('changes_requested', 'Modifications demandées'),
        ('approved', 'Approuvé'),
        ('scheduled', 'Programmé'),
        ('published', 'Publié'),
        ('archived', 'Archivé'),
        ('deactivated', 'Désactivé'),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=PAGE_STATUS_CHOICES,
        default='draft'
    )
    
    status_changed_at = models.DateTimeField(auto_now_add=True)
    status_changed_by = models.ForeignKey(
        'users_core.CustomUser',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    
    production_notes = models.TextField(
        blank=True,
        help_text="Notes internes pour l'équipe"
    )
    
    def get_status_color(self):
        """Couleur pour l'UI selon le statut"""
        status_colors = {
            'draft': '#6c757d',
            'in_progress': '#007bff',
            'pending_review': '#ffc107',
            'under_review': '#fd7e14',
            'changes_requested': '#dc3545',
            'approved': '#28a745',
            'scheduled': '#17a2b8',
            'published': '#20c997',
            'archived': '#6f42c1',
            'deactivated': '#495057',
        }
        return status_colors.get(self.status, '#6c757d')
    
    def get_next_possible_statuses(self):
        """Statuts suivants possibles selon le workflow"""
        transitions = {
            'draft': ['in_progress', 'pending_review', 'archived'],
            'in_progress': ['pending_review', 'draft'],
            'pending_review': ['under_review', 'approved', 'changes_requested'],
            'under_review': ['approved', 'changes_requested', 'pending_review'],
            'changes_requested': ['in_progress', 'pending_review'],
            'approved': ['published', 'scheduled', 'pending_review'],
            'scheduled': ['published', 'approved'],
            'published': ['archived', 'deactivated', 'approved'],
            'archived': ['draft', 'deactivated'],
            'deactivated': ['draft', 'approved', 'archived'],
        }
        return transitions.get(self.status, [])
    
    def can_be_published(self):
        """Vérifie si la page peut être publiée"""
        return self.status in ['approved', 'scheduled']
    
    def is_publicly_accessible(self):
        """Vérifie si la page peut être affichée publiquement"""
        return self.status == 'published'
    
    def update_status(self, new_status, user=None, notes=""):
        """Met à jour le statut avec traçabilité"""
        old_status = self.status
        self.status = new_status
        self.status_changed_by = user
        self.status_changed_at = timezone.now()
        
        if notes:
            if self.production_notes:
                self.production_notes += f"\n---\n{notes}"
            else:
                self.production_notes = notes
        
        self.save(update_fields=['status', 'status_changed_by', 'status_changed_at', 'production_notes'])
        logger.info(f"Page {self.page.id} status: {old_status} → {new_status} by {user}")
    
    def __str__(self):
        return f"{self.page.title} - {self.get_status_display()}"
    
    class Meta:
        db_table = 'seo_pages_workflow_status'
        ordering = ['-status_changed_at']  # 🔧 AJOUTER CETTE LIGNE
        verbose_name = "Statut de Page"
        verbose_name_plural = "Statuts de Page"
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['status_changed_at']),
        ]
