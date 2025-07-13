# backend/ai_core/models/core_models.py

import uuid  # 🆕 Import nécessaire
from django.db import models
from common.models.mixins import TimestampedMixin, BrandScopedMixin

# 🆕 Fonction pour générer job_id unique
def generate_job_id():
    return f"ai_{uuid.uuid4().hex[:12]}"

class AIJobType(TimestampedMixin):
    """Type de job IA disponible"""
    # ❌ SUPPRIMER ces 2 lignes
    # job_id = models.CharField(max_length=100, unique=True, blank=True)
    # def save(self, *args, **kwargs): ...
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=[
        ('chat', 'Chat Completion'),
        ('assistant', 'Assistant'),
        ('upload', 'File Upload'),
        ('analysis', 'Analysis'),
        ('generation', 'Content Generation')
    ])
    estimated_duration_seconds = models.IntegerField(default=30)
    requires_async = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'ai_job_type'
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.category})"

class AIJobStatus(models.TextChoices):
    """Statuts possibles d'un job IA"""
    PENDING = 'pending', 'En attente'
    RUNNING = 'running', 'En cours'
    COMPLETED = 'completed', 'Terminé'
    FAILED = 'failed', 'Échoué'
    CANCELLED = 'cancelled', 'Annulé'
    TIMEOUT = 'timeout', 'Timeout'

class AIJob(TimestampedMixin, BrandScopedMixin):
    """Job IA central - référencé par extensions providers"""
    job_id = models.CharField(
        max_length=100, 
        unique=True,
        default=generate_job_id  # 🆕 AJOUTER ça ici
    )
    job_type = models.ForeignKey(AIJobType, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=AIJobStatus.choices,
        default=AIJobStatus.PENDING
    )
    
    # ... reste du modèle inchangé
    
    # Contexte
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=20, choices=[
        ('low', 'Basse'),
        ('normal', 'Normale'),
        ('high', 'Haute'),
        ('urgent', 'Urgente')
    ], default='normal')
    
    # Données job
    input_data = models.JSONField(default=dict)
    result_data = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    
    # Tracking
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    progress_percentage = models.IntegerField(default=0)
    
    # Task core integration
    task_id = models.CharField(max_length=100, blank=True)
    is_async = models.BooleanField(default=False)
    
    # Metadata
    created_by = models.ForeignKey(
        'users_core.CustomUser',
        on_delete=models.CASCADE,
        related_name='ai_jobs'
    )
    
    class Meta:
        db_table = 'ai_job'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['brand', 'status']),
            models.Index(fields=['job_id']),
        ]
    
    def __str__(self):
        return f"AIJob {self.job_id} - {self.job_type.name}"