# backend/task_core/models/base_models.py

import uuid
from django.db import models
from django.contrib.auth import get_user_model
from common.models.mixins import TimestampedMixin, BrandScopedMixin

User = get_user_model()

class BaseTask(TimestampedMixin, BrandScopedMixin):
    """
    Modèle central pour toutes les tâches Celery - Hub infrastructure
    Pattern extension : autres apps font OneToOne vers ce modèle
    """
    
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('processing', 'En cours'),
        ('completed', 'Terminé'),
        ('failed', 'Échoué'),
        ('cancelled', 'Annulé'),
        ('retry', 'En attente de retry'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Basse'),
        ('normal', 'Normale'), 
        ('high', 'Haute'),
        ('critical', 'Critique'),
    ]
    
    # Identifiants
    task_id = models.CharField(max_length=255, unique=True, db_index=True)
    celery_task_id = models.CharField(max_length=255, null=True, blank=True)
    task_type = models.CharField(max_length=100, db_index=True)
    
    # État et configuration
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    queue_name = models.CharField(max_length=50, default='normal')
    
    # Métadonnées
    description = models.TextField(blank=True)
    context_data = models.JSONField(default=dict, blank=True)
    
    # Utilisateur et traçabilité
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    
    class Meta:
        db_table = 'task_base'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['task_type', 'status']),
            models.Index(fields=['brand', 'status']),
            models.Index(fields=['celery_task_id']),
            models.Index(fields=['priority', 'status']),  # Pour queue management
        ]
        
    def save(self, *args, **kwargs):
        """Auto-génère task_id si absent"""
        if not self.task_id:
            # Générer un ID unique basé sur task_type + UUID
            unique_suffix = str(uuid.uuid4())[:8]
            self.task_id = f"{self.task_type}_{unique_suffix}"
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.task_type} - {self.task_id}"
    
    def mark_as_processing(self, celery_task_id: str = None):
        """Marque la tâche comme en cours de traitement"""
        self.status = 'processing'
        if celery_task_id:
            self.celery_task_id = celery_task_id
        self.save(update_fields=['status', 'celery_task_id'])
    
    def mark_as_completed(self):
        """Marque la tâche comme terminée"""
        self.status = 'completed'
        self.save(update_fields=['status'])
    
    def mark_as_failed(self, error_message: str = None):
        """Marque la tâche comme échouée"""
        self.status = 'failed'
        if error_message:
            context_data = self.context_data or {}
            context_data['error_message'] = error_message
            self.context_data = context_data
        self.save(update_fields=['status', 'context_data'])
    
    def can_retry(self) -> bool:
        """Vérifie si la tâche peut être relancée"""
        return self.status in ['failed', 'cancelled']
    
    def get_queue_for_priority(self) -> str:
        """Retourne la queue selon la priorité"""
        priority_queue_map = {
            'critical': 'high_priority',
            'high': 'high_priority', 
            'normal': 'normal',
            'low': 'low_priority',
        }
        return priority_queue_map.get(self.priority, 'normal')