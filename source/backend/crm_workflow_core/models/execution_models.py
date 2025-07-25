# /var/www/megahub/backend/crm_workflow_core/models/execution_models.py
import uuid
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from .base_models import WorkflowBaseMixin

class WorkflowExecution(WorkflowBaseMixin):
    """Exécution d'un workflow sur un enregistrement"""
    
    EXECUTION_STATUS = [
        ('pending', 'En attente'),
        ('running', 'En cours'),
        ('paused', 'En pause'),
        ('completed', 'Terminé'),
        ('failed', 'Échoué'),
        ('cancelled', 'Annulé'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(
        'crm_workflow_core.Workflow',
        on_delete=models.CASCADE,
        related_name='executions',
        help_text="Workflow exécuté"
    )
    
    # Enregistrement cible
    target_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        help_text="Type d'enregistrement cible"
    )
    target_object_id = models.UUIDField(
        help_text="ID de l'enregistrement cible"
    )
    target_object = GenericForeignKey('target_content_type', 'target_object_id')
    
    # État d'exécution
    status = models.CharField(
        max_length=15,
        choices=EXECUTION_STATUS,
        default='pending',
        help_text="Statut d'exécution"
    )
    current_step = models.ForeignKey(
        'crm_workflow_core.WorkflowStep',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Étape actuelle"
    )
    
    # Dates
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Démarrage"
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Completion"
    )
    next_execution_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Prochaine exécution programmée"
    )
    
    # Contexte d'exécution
    execution_context = models.JSONField(
        default=dict,
        help_text="Contexte d'exécution (variables, état)"
    )
    trigger_context = models.JSONField(
        default=dict,
        help_text="Contexte du déclenchement"
    )
    
    # Résultats
    result_summary = models.JSONField(
        default=dict,
        blank=True,
        help_text="Résumé des résultats"
    )
    error_message = models.TextField(
        blank=True,
        help_text="Message d'erreur si échec"
    )
    
    # Statistiques
    steps_completed = models.IntegerField(
        default=0,
        help_text="Nombre d'étapes terminées"
    )
    steps_failed = models.IntegerField(
        default=0,
        help_text="Nombre d'étapes échouées"
    )
    
    class Meta:
        db_table = 'crm_workflow_execution'
        ordering = ['-created_at']
        verbose_name = 'Exécution Workflow'
        verbose_name_plural = 'Exécutions Workflow'
        indexes = [
            models.Index(fields=['workflow', 'status']),
            models.Index(fields=['target_content_type', 'target_object_id']),
            models.Index(fields=['status', 'next_execution_at']),
            models.Index(fields=['started_at', 'completed_at']),
        ]
    
    def __str__(self):
        return f"{self.workflow.name} - {self.target_object} ({self.status})"
    
    @property
    def duration_seconds(self):
        """Durée d'exécution en secondes"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    @property
    def is_running(self):
        """Vérifie si l'exécution est en cours"""
        return self.status in ['pending', 'running', 'paused']
    
    def start_execution(self):
        """Démarre l'exécution"""
        from django.utils import timezone
        self.status = 'running'
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at'])
    
    def complete_execution(self, success=True):
        """Termine l'exécution"""
        from django.utils import timezone
        self.status = 'completed' if success else 'failed'
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at'])

class WorkflowStepExecution(WorkflowBaseMixin):
    """Exécution d'une étape de workflow"""
    
    STEP_EXECUTION_STATUS = [
        ('pending', 'En attente'),
        ('running', 'En cours'),
        ('completed', 'Terminé'),
        ('failed', 'Échoué'),
        ('skipped', 'Ignoré'),
        ('waiting', 'En attente délai'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_execution = models.ForeignKey(
        WorkflowExecution,
        on_delete=models.CASCADE,
        related_name='step_executions',
        help_text="Exécution workflow parent"
    )
    workflow_step = models.ForeignKey(
        'crm_workflow_core.WorkflowStep',
        on_delete=models.CASCADE,
        related_name='executions',
        help_text="Étape exécutée"
    )
    
    # État
    status = models.CharField(
        max_length=15,
        choices=STEP_EXECUTION_STATUS,
        default='pending',
        help_text="Statut d'exécution"
    )
    
    # Dates
    scheduled_at = models.DateTimeField(
        help_text="Programmé pour"
    )
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Démarrage"
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Completion"
    )
    
    # Résultats
    execution_result = models.JSONField(
        default=dict,
        blank=True,
        help_text="Résultat de l'exécution"
    )
    error_details = models.TextField(
        blank=True,
        help_text="Détails de l'erreur"
    )
    
    # Tentatives
    attempt_number = models.IntegerField(
        default=1,
        help_text="Numéro de tentative"
    )
    max_retries = models.IntegerField(
        default=3,
        help_text="Nombre max de tentatives"
    )
    
    class Meta:
        db_table = 'crm_workflow_step_execution'
        ordering = ['workflow_execution', 'workflow_step__step_order']
        verbose_name = 'Exécution Étape'
        verbose_name_plural = 'Exécutions Étapes'
        indexes = [
            models.Index(fields=['workflow_execution', 'status']),
            models.Index(fields=['workflow_step', 'status']),
            models.Index(fields=['scheduled_at', 'status']),
        ]
    
    def __str__(self):
        return f"{self.workflow_step.name} - {self.status}"
    
    @property
    def can_retry(self):
        """Vérifie si on peut retenter"""
        return self.status == 'failed' and self.attempt_number < self.max_retries
