# /var/www/megahub/backend/crm_workflow_core/models/workflow_models.py
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .base_models import WorkflowBaseMixin

class Workflow(WorkflowBaseMixin):
    """Workflow CRM automatisé"""
    
    WORKFLOW_TYPES = [
        ('lead_nurturing', 'Nurturing Leads'),
        ('deal_progression', 'Progression Affaires'),
        ('onboarding', 'Onboarding Client'),
        ('support', 'Support Client'),
        ('renewal', 'Renouvellement'),
        ('upsell', 'Montée en Gamme'),
        ('data_quality', 'Qualité Données'),
        ('reporting', 'Reporting'),
        ('custom', 'Personnalisé'),
    ]
    
    TRIGGER_EVENTS = [
        ('manual', 'Manuel'),
        ('record_created', 'Enregistrement Créé'),
        ('record_updated', 'Enregistrement Mis à Jour'),
        ('field_changed', 'Champ Modifié'),
        ('stage_changed', 'Étape Modifiée'),
        ('date_reached', 'Date Atteinte'),
        ('activity_completed', 'Activité Terminée'),
        ('email_opened', 'Email Ouvert'),
        ('form_submitted', 'Formulaire Soumis'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=100,
        help_text="Nom du workflow"
    )
    
    # Classification
    workflow_type = models.CharField(
        max_length=20,
        choices=WORKFLOW_TYPES,
        help_text="Type de workflow"
    )
    description = models.TextField(
        blank=True,
        help_text="Description du workflow"
    )
    
    # Déclenchement
    trigger_event = models.CharField(
        max_length=20,
        choices=TRIGGER_EVENTS,
        help_text="Événement déclencheur"
    )
    trigger_object = models.CharField(
        max_length=50,
        help_text="Objet déclencheur (Account, Contact, etc.)"
    )
    trigger_conditions = models.JSONField(
        default=dict,
        blank=True,
        help_text="Conditions de déclenchement en JSON"
    )
    
    # Configuration
    is_active = models.BooleanField(
        default=True,
        help_text="Workflow actif"
    )
    is_automatic = models.BooleanField(
        default=True,
        help_text="Exécution automatique"
    )
    execution_order = models.IntegerField(
        default=0,
        help_text="Ordre d'exécution si plusieurs workflows"
    )
    
    # Limites et contrôle
    max_executions_per_record = models.IntegerField(
        null=True,
        blank=True,
        help_text="Nombre max d'exécutions par enregistrement"
    )
    execution_interval_hours = models.IntegerField(
        null=True,
        blank=True,
        help_text="Intervalle minimum entre exécutions (heures)"
    )
    
    # Statistiques
    total_executions = models.IntegerField(
        default=0,
        help_text="Nombre total d'exécutions"
    )
    successful_executions = models.IntegerField(
        default=0,
        help_text="Exécutions réussies"
    )
    failed_executions = models.IntegerField(
        default=0,
        help_text="Exécutions échouées"
    )
    last_execution_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Dernière exécution"
    )
    
    class Meta:
        db_table = 'crm_workflow'
        ordering = ['execution_order', 'name']
        verbose_name = 'Workflow CRM'
        verbose_name_plural = 'Workflows CRM'
        indexes = [
            models.Index(fields=['workflow_type', 'is_active']),
            models.Index(fields=['trigger_event', 'trigger_object']),
            models.Index(fields=['execution_order']),
            models.Index(fields=['last_execution_date']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_workflow_type_display()})"
    
    @property
    def success_rate(self):
        """Taux de succès des exécutions"""
        if self.total_executions == 0:
            return 0
        return (self.successful_executions / self.total_executions) * 100
    
    def get_steps_count(self):
        """Nombre d'étapes dans le workflow"""
        return self.steps.count()
    
    def increment_execution_stats(self, success=True):
        """Incrémente les statistiques d'exécution"""
        from django.utils import timezone
        
        self.total_executions += 1
        if success:
            self.successful_executions += 1
        else:
            self.failed_executions += 1
        self.last_execution_date = timezone.now()
        
        self.save(update_fields=[
            'total_executions', 'successful_executions', 
            'failed_executions', 'last_execution_date'
        ])

class WorkflowStep(WorkflowBaseMixin):
    """Étape dans un workflow"""
    
    STEP_TYPES = [
        ('condition', 'Condition'),
        ('action', 'Action'),
        ('wait', 'Attente'),
        ('email', 'Envoi Email'),
        ('task', 'Créer Tâche'),
        ('update_field', 'Mettre à Jour Champ'),
        ('webhook', 'Webhook'),
        ('approval', 'Approbation'),
        ('notification', 'Notification'),
        ('branch', 'Embranchement'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(
        Workflow,
        on_delete=models.CASCADE,
        related_name='steps',
        help_text="Workflow parent"
    )
    name = models.CharField(
        max_length=100,
        help_text="Nom de l'étape"
    )
    
    # Position et type
    step_type = models.CharField(
        max_length=20,
        choices=STEP_TYPES,
        help_text="Type d'étape"
    )
    step_order = models.IntegerField(
        help_text="Ordre d'exécution"
    )
    
    # Configuration
    step_config = models.JSONField(
        default=dict,
        help_text="Configuration spécifique de l'étape"
    )
    conditions = models.JSONField(
        default=dict,
        blank=True,
        help_text="Conditions d'exécution de l'étape"
    )
    
    # Délais
    delay_hours = models.IntegerField(
        default=0,
        help_text="Délai avant exécution (heures)"
    )
    delay_business_hours_only = models.BooleanField(
        default=False,
        help_text="Délai en heures ouvrées uniquement"
    )
    
    # Branchement
    next_step_success = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='success_predecessors',
        help_text="Étape suivante si succès"
    )
    next_step_failure = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='failure_predecessors',
        help_text="Étape suivante si échec"
    )
    
    # État
    is_active = models.BooleanField(
        default=True,
        help_text="Étape active"
    )
    description = models.TextField(
        blank=True,
        help_text="Description de l'étape"
    )
    
    # Statistiques
    execution_count = models.IntegerField(
        default=0,
        help_text="Nombre d'exécutions"
    )
    success_count = models.IntegerField(
        default=0,
        help_text="Succès"
    )
    failure_count = models.IntegerField(
        default=0,
        help_text="Échecs"
    )
    
    class Meta:
        db_table = 'crm_workflow_step'
        unique_together = ['workflow', 'step_order']
        ordering = ['workflow', 'step_order']
        verbose_name = 'Étape Workflow'
        verbose_name_plural = 'Étapes Workflow'
        indexes = [
            models.Index(fields=['workflow', 'step_order']),
            models.Index(fields=['step_type', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.workflow.name} - {self.name} (#{self.step_order})"
    
    @property
    def success_rate(self):
        """Taux de succès de l'étape"""
        if self.execution_count == 0:
            return 0
        return (self.success_count / self.execution_count) * 100
    
    def increment_execution_stats(self, success=True):
        """Incrémente les statistiques d'exécution"""
        self.execution_count += 1
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
        self.save(update_fields=['execution_count', 'success_count', 'failure_count'])
