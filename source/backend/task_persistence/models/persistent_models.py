# backend/task_persistence/models/persistent_models.py

from django.db import models
from django.contrib.auth import get_user_model
from common.models.mixins import TimestampedMixin
from task_core.models import BaseTask
import json

User = get_user_model()

class PersistentJob(TimestampedMixin):
    """
    Extension OneToOne de BaseTask pour jobs persistants avec reprise
    Remplace ContentGenerationJob legacy
    """
    
    # Relation vers BaseTask (hub central)
    base_task = models.OneToOneField(
        BaseTask, 
        on_delete=models.CASCADE, 
        related_name='persistent_job'
    )
    
    # Données du job
    job_data = models.JSONField(default=dict, help_text="Configuration du job")
    current_step = models.CharField(max_length=100, default='init')
    total_steps = models.PositiveIntegerField(default=1)
    completed_steps = models.PositiveIntegerField(default=0)
    
    # État de reprise
    can_resume = models.BooleanField(default=True)
    resume_from_step = models.CharField(max_length=100, blank=True)
    last_checkpoint_at = models.DateTimeField(null=True, blank=True)
    
    # Métriques
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    estimated_remaining_minutes = models.PositiveIntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'task_persistent_job'
        indexes = [
            models.Index(fields=['can_resume', 'current_step']),
            models.Index(fields=['base_task', 'last_checkpoint_at']),
        ]
        
    def __str__(self):
        return f"PersistentJob: {self.base_task.task_id}"
    
    def mark_step_completed(self, step_name: str):
        """Marque une étape comme terminée"""
        self.completed_steps += 1
        self.current_step = step_name
        self.progress_percentage = (self.completed_steps / self.total_steps) * 100
        self.save(update_fields=['completed_steps', 'current_step', 'progress_percentage'])
    
    def create_checkpoint(self, checkpoint_data: dict):
        """Crée un point de sauvegarde"""
        from django.utils import timezone
        
        JobCheckpoint.objects.create(
            persistent_job=self,
            step_name=self.current_step,
            checkpoint_data=checkpoint_data
        )
        
        self.last_checkpoint_at = timezone.now()
        self.save(update_fields=['last_checkpoint_at'])
    
    def get_latest_checkpoint(self):
        """Récupère le dernier checkpoint"""
        return self.checkpoints.order_by('-created_at').first()
    
    def is_resumable(self) -> bool:
        """Vérifie si le job peut être repris"""
        return (
            self.can_resume and 
            self.base_task.status in ['failed', 'cancelled'] and
            self.completed_steps > 0
        )

class JobCheckpoint(TimestampedMixin):
    """Points de sauvegarde pour reprise de jobs"""
    
    persistent_job = models.ForeignKey(
        PersistentJob, 
        on_delete=models.CASCADE, 
        related_name='checkpoints'
    )
    
    step_name = models.CharField(max_length=100)
    checkpoint_data = models.JSONField(default=dict)
    is_recovery_point = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'task_job_checkpoint'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['persistent_job', 'step_name']),
            models.Index(fields=['is_recovery_point', 'created_at']),
        ]
        
    def __str__(self):
        return f"Checkpoint: {self.step_name} - {self.created_at}"

class JobState(TimestampedMixin):
    """État détaillé pour jobs complexes (ex: génération de contenu)"""
    
    persistent_job = models.OneToOneField(
        PersistentJob, 
        on_delete=models.CASCADE, 
        related_name='job_state'
    )
    
    # État spécifique par type de job
    pages_status = models.JSONField(default=dict, help_text="Statut par page")
    error_log = models.JSONField(default=list, help_text="Log des erreurs")
    warnings = models.JSONField(default=list, help_text="Avertissements")
    
    # Métriques avancées
    retry_count = models.PositiveIntegerField(default=0)
    max_retries = models.PositiveIntegerField(default=3)
    last_error_message = models.TextField(blank=True)
    
    class Meta:
        db_table = 'task_job_state'
        
    def __str__(self):
        return f"JobState: {self.persistent_job.base_task.task_id}"
    
    def add_error(self, error_message: str, page_id: int = None):
        """Ajoute une erreur au log"""
        from django.utils import timezone
        
        error_entry = {
            'timestamp': timezone.now().isoformat(),
            'message': error_message,
            'page_id': page_id
        }
        
        self.error_log.append(error_entry)
        self.last_error_message = error_message
        self.save(update_fields=['error_log', 'last_error_message'])
    
    def can_retry(self) -> bool:
        """Vérifie si le job peut être relancé"""
        return self.retry_count < self.max_retries
