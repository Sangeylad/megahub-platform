# /var/www/megahub/backend/crm_pipeline_automation/models/automation_models.py
import uuid
from django.db import models
from crm_entities_core.models import CRMBaseMixin

class PipelineRule(CRMBaseMixin):
    """Règles d'automatisation des pipelines"""
    
    TRIGGER_TYPES = [
        ('stage_entry', 'Entrée dans étape'),
        ('stage_exit', 'Sortie d\'étape'),
        ('time_based', 'Basé sur le temps'),
        ('field_change', 'Changement de champ'),
        ('amount_threshold', 'Seuil montant'),
        ('probability_change', 'Changement probabilité'),
        ('activity_created', 'Activité créée'),
        ('no_activity', 'Absence d\'activité'),
    ]
    
    ACTION_TYPES = [
        ('move_stage', 'Déplacer vers étape'),
        ('assign_user', 'Assigner utilisateur'),
        ('send_email', 'Envoyer email'),
        ('create_task', 'Créer tâche'),
        ('update_field', 'Mettre à jour champ'),
        ('send_notification', 'Envoyer notification'),
        ('create_activity', 'Créer activité'),
        ('webhook', 'Webhook'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=100,
        help_text="Nom de la règle"
    )
    
    # Scope
    pipeline = models.ForeignKey(
        'crm_pipeline_core.Pipeline',
        on_delete=models.CASCADE,
        related_name='automation_rules',
        null=True,
        blank=True,
        help_text="Pipeline spécifique (null = toutes)"
    )
    stage = models.ForeignKey(
        'crm_pipeline_core.Stage',
        on_delete=models.CASCADE,
        related_name='automation_rules',
        null=True,
        blank=True,
        help_text="Étape spécifique (null = toutes)"
    )
    
    # Déclencheur
    trigger_type = models.CharField(
        max_length=20,
        choices=TRIGGER_TYPES,
        help_text="Type de déclencheur"
    )
    trigger_conditions = models.JSONField(
        default=dict,
        help_text="Conditions du déclencheur en JSON"
    )
    
    # Action
    action_type = models.CharField(
        max_length=20,
        choices=ACTION_TYPES,
        help_text="Type d'action"
    )
    action_config = models.JSONField(
        default=dict,
        help_text="Configuration de l'action en JSON"
    )
    
    # Timing
    delay_minutes = models.IntegerField(
        default=0,
        help_text="Délai avant exécution (minutes)"
    )
    business_hours_only = models.BooleanField(
        default=False,
        help_text="Exécuter uniquement en heures ouvrées"
    )
    
    # Conditions supplémentaires
    additional_conditions = models.JSONField(
        default=dict,
        blank=True,
        help_text="Conditions supplémentaires"
    )
    
    # Configuration
    is_active = models.BooleanField(
        default=True,
        help_text="Règle active"
    )
    priority = models.IntegerField(
        default=0,
        help_text="Priorité d'exécution"
    )
    
    # Statistiques
    execution_count = models.IntegerField(
        default=0,
        help_text="Nombre d'exécutions"
    )
    success_count = models.IntegerField(
        default=0,
        help_text="Exécutions réussies"
    )
    last_execution = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Dernière exécution"
    )
    
    # Description
    description = models.TextField(
        blank=True,
        help_text="Description de la règle"
    )
    
    class Meta:
        db_table = 'crm_pipeline_rule'
        ordering = ['priority', 'name']
        verbose_name = 'Règle Pipeline'
        verbose_name_plural = 'Règles Pipeline'
        indexes = [
            models.Index(fields=['pipeline', 'is_active']),
            models.Index(fields=['stage', 'is_active']),
            models.Index(fields=['trigger_type']),
            models.Index(fields=['priority']),
        ]
    
    def __str__(self):
        scope = ""
        if self.pipeline:
            scope = f" ({self.pipeline.name})"
        if self.stage:
            scope += f" - {self.stage.name}"
        return f"{self.name}{scope}"
    
    @property
    def success_rate(self):
        """Taux de succès des exécutions"""
        if self.execution_count == 0:
            return 0
        return (self.success_count / self.execution_count) * 100
    
    def increment_execution_stats(self, success=True):
        """Incrémente les statistiques d'exécution"""
        from django.utils import timezone
        
        self.execution_count += 1
        if success:
            self.success_count += 1
        self.last_execution = timezone.now()
        self.save(update_fields=['execution_count', 'success_count', 'last_execution'])

class RuleExecution(CRMBaseMixin):
    """Historique d'exécution des règles"""
    
    EXECUTION_STATUS = [
        ('pending', 'En attente'),
        ('running', 'En cours'),
        ('success', 'Succès'),
        ('failed', 'Échec'),
        ('skipped', 'Ignoré'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relations
    rule = models.ForeignKey(
        PipelineRule,
        on_delete=models.CASCADE,
        related_name='executions',
        help_text="Règle exécutée"
    )
    opportunity = models.ForeignKey(
        'crm_entities_core.Opportunity',
        on_delete=models.CASCADE,
        related_name='rule_executions',
        help_text="Opportunité concernée"
    )
    
    # Exécution
    status = models.CharField(
        max_length=15,
        choices=EXECUTION_STATUS,
        default='pending',
        help_text="Statut d'exécution"
    )
    scheduled_at = models.DateTimeField(
        help_text="Programmé pour"
    )
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Démarré à"
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Terminé à"
    )
    
    # Contexte
    trigger_context = models.JSONField(
        default=dict,
        help_text="Contexte du déclenchement"
    )
    execution_result = models.JSONField(
        default=dict,
        blank=True,
        help_text="Résultat de l'exécution"
    )
    
    # Erreurs
    error_message = models.TextField(
        blank=True,
        help_text="Message d'erreur si échec"
    )
    retry_count = models.IntegerField(
        default=0,
        help_text="Nombre de tentatives"
    )
    
    class Meta:
        db_table = 'crm_rule_execution'
        ordering = ['-scheduled_at']
        verbose_name = 'Exécution Règle'
        verbose_name_plural = 'Exécutions Règles'
        indexes = [
            models.Index(fields=['rule', 'status']),
            models.Index(fields=['opportunity', 'scheduled_at']),
            models.Index(fields=['status', 'scheduled_at']),
        ]
    
    def __str__(self):
        return f"{self.rule.name} - {self.opportunity.name} ({self.status})"
    
    @property
    def execution_duration(self):
        """Durée d'exécution en secondes"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

class AutomationTrigger(CRMBaseMixin):
    """Déclencheurs d'automatisation configurables"""
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=100,
        help_text="Nom du déclencheur"
    )
    
    # Configuration
    event_type = models.CharField(
        max_length=50,
        help_text="Type d'événement"
    )
    conditions = models.JSONField(
        default=dict,
        help_text="Conditions de déclenchement"
    )
    
    # Règles associées
    rules = models.ManyToManyField(
        PipelineRule,
        related_name='triggers',
        blank=True,
        help_text="Règles déclenchées"
    )
    
    # Statut
    is_active = models.BooleanField(
        default=True,
        help_text="Déclencheur actif"
    )
    
    class Meta:
        db_table = 'crm_automation_trigger'
        ordering = ['name']
        verbose_name = 'Déclencheur Automatisation'
        verbose_name_plural = 'Déclencheurs Automatisation'
        indexes = [
            models.Index(fields=['event_type', 'is_active']),
        ]
    
    def __str__(self):
        return self.name
