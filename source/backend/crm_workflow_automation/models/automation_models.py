# /var/www/megahub/backend/crm_workflow_automation/models/automation_models.py
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from crm_workflow_core.models import WorkflowBaseMixin

class WorkflowTrigger(WorkflowBaseMixin):
    """Déclencheurs de workflow"""
    
    TRIGGER_TYPES = [
        ('field_change', 'Changement de Champ'),
        ('record_created', 'Enregistrement Créé'),
        ('record_updated', 'Enregistrement Mis à Jour'),
        ('stage_change', 'Changement d\'Étape'),
        ('date_time', 'Date/Heure'),
        ('activity_completed', 'Activité Terminée'),
        ('email_interaction', 'Interaction Email'),
        ('form_submission', 'Soumission Formulaire'),
        ('api_call', 'Appel API'),
        ('webhook', 'Webhook'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=100,
        help_text="Nom du déclencheur"
    )
    
    # Configuration
    trigger_type = models.CharField(
        max_length=20,
        choices=TRIGGER_TYPES,
        help_text="Type de déclencheur"
    )
    target_object = models.CharField(
        max_length=50,
        help_text="Objet surveillé (Account, Contact, etc.)"
    )
    trigger_conditions = models.JSONField(
        default=dict,
        help_text="Conditions de déclenchement"
    )
    
    # Workflows associés
    workflows = models.ManyToManyField(
        'crm_workflow_core.Workflow',
        through='TriggerWorkflowAssociation',
        related_name='triggers',
        help_text="Workflows déclenchés"
    )
    
    # Limitations
    max_executions_per_hour = models.IntegerField(
        null=True,
        blank=True,
        help_text="Limite d'exécutions par heure"
    )
    cooldown_minutes = models.IntegerField(
        default=0,
        help_text="Délai de refroidissement (minutes)"
    )
    
    # Statut
    is_active = models.BooleanField(
        default=True,
        help_text="Déclencheur actif"
    )
    
    # Statistiques
    trigger_count = models.IntegerField(
        default=0,
        help_text="Nombre de déclenchements"
    )
    last_triggered_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Dernier déclenchement"
    )
    
    class Meta:
        db_table = 'crm_workflow_trigger'
        ordering = ['name']
        verbose_name = 'Déclencheur Workflow'
        verbose_name_plural = 'Déclencheurs Workflow'
        indexes = [
            models.Index(fields=['trigger_type', 'target_object']),
            models.Index(fields=['is_active']),
            models.Index(fields=['last_triggered_at']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_trigger_type_display()})"

class TriggerWorkflowAssociation(models.Model):
    """Association entre déclencheurs et workflows"""
    
    # Relations
    trigger = models.ForeignKey(
        WorkflowTrigger,
        on_delete=models.CASCADE,
        help_text="Déclencheur"
    )
    workflow = models.ForeignKey(
        'crm_workflow_core.Workflow',
        on_delete=models.CASCADE,
        help_text="Workflow"
    )
    
    # Configuration
    priority = models.IntegerField(
        default=0,
        help_text="Priorité d'exécution"
    )
    conditions = models.JSONField(
        default=dict,
        blank=True,
        help_text="Conditions supplémentaires"
    )
    delay_minutes = models.IntegerField(
        default=0,
        help_text="Délai avant déclenchement (minutes)"
    )
    
    # Statut
    is_active = models.BooleanField(
        default=True,
        help_text="Association active"
    )
    
    class Meta:
        db_table = 'crm_trigger_workflow_association'
        unique_together = ['trigger', 'workflow']
        ordering = ['priority']
        verbose_name = 'Association Trigger-Workflow'
        verbose_name_plural = 'Associations Trigger-Workflow'
    
    def __str__(self):
        return f"{self.trigger.name} → {self.workflow.name}"

class WorkflowCondition(WorkflowBaseMixin):
    """Conditions pour workflows"""
    
    CONDITION_TYPES = [
        ('field_value', 'Valeur de Champ'),
        ('field_comparison', 'Comparaison de Champs'),
        ('date_condition', 'Condition de Date'),
        ('count_condition', 'Condition de Comptage'),
        ('relationship_exists', 'Relation Existe'),
        ('custom_formula', 'Formule Personnalisée'),
        ('time_based', 'Basé sur le Temps'),
        ('user_condition', 'Condition Utilisateur'),
    ]
    
    OPERATORS = [
        ('equals', 'Égal'),
        ('not_equals', 'Différent'),
        ('greater_than', 'Supérieur à'),
        ('less_than', 'Inférieur à'),
        ('greater_equal', 'Supérieur ou égal'),
        ('less_equal', 'Inférieur ou égal'),
        ('contains', 'Contient'),
        ('starts_with', 'Commence par'),
        ('ends_with', 'Finit par'),
        ('in_list', 'Dans la liste'),
        ('is_empty', 'Est vide'),
        ('is_not_empty', 'N\'est pas vide'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=100,
        help_text="Nom de la condition"
    )
    
    # Configuration
    condition_type = models.CharField(
        max_length=20,
        choices=CONDITION_TYPES,
        help_text="Type de condition"
    )
    field_name = models.CharField(
        max_length=100,
        help_text="Nom du champ"
    )
    operator = models.CharField(
        max_length=15,
        choices=OPERATORS,
        help_text="Opérateur de comparaison"
    )
    expected_value = models.TextField(
        blank=True,
        help_text="Valeur attendue"
    )
    
    # Configuration avancée
    condition_logic = models.JSONField(
        default=dict,
        blank=True,
        help_text="Logique de condition complexe"
    )
    custom_formula = models.TextField(
        blank=True,
        help_text="Formule personnalisée"
    )
    
    # Statut
    is_active = models.BooleanField(
        default=True,
        help_text="Condition active"
    )
    
    class Meta:
        db_table = 'crm_workflow_condition'
        ordering = ['name']
        verbose_name = 'Condition Workflow'
        verbose_name_plural = 'Conditions Workflow'
        indexes = [
            models.Index(fields=['condition_type']),
            models.Index(fields=['field_name']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.field_name} {self.get_operator_display()})"

class WorkflowAction(WorkflowBaseMixin):
    """Actions pour workflows"""
    
    ACTION_TYPES = [
        ('update_field', 'Mettre à Jour Champ'),
        ('create_record', 'Créer Enregistrement'),
        ('send_email', 'Envoyer Email'),
        ('create_task', 'Créer Tâche'),
        ('create_activity', 'Créer Activité'),
        ('assign_user', 'Assigner Utilisateur'),
        ('change_stage', 'Changer Étape'),
        ('send_notification', 'Envoyer Notification'),
        ('webhook_call', 'Appel Webhook'),
        ('api_request', 'Requête API'),
        ('run_script', 'Exécuter Script'),
        ('wait_delay', 'Attendre'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=100,
        help_text="Nom de l'action"
    )
    
    # Configuration
    action_type = models.CharField(
        max_length=20,
        choices=ACTION_TYPES,
        help_text="Type d'action"
    )
    action_config = models.JSONField(
        default=dict,
        help_text="Configuration de l'action"
    )
    
    # Templates et contenu
    email_template = models.TextField(
        blank=True,
        help_text="Template email"
    )
    notification_message = models.TextField(
        blank=True,
        help_text="Message de notification"
    )
    
    # Conditions d'exécution
    execution_conditions = models.JSONField(
        default=dict,
        blank=True,
        help_text="Conditions d'exécution"
    )
    
    # Retry et erreur
    max_retries = models.IntegerField(
        default=3,
        help_text="Nombre max de tentatives"
    )
    retry_delay_minutes = models.IntegerField(
        default=5,
        help_text="Délai entre tentatives (minutes)"
    )
    
    # Statut
    is_active = models.BooleanField(
        default=True,
        help_text="Action active"
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
        db_table = 'crm_workflow_action'
        ordering = ['name']
        verbose_name = 'Action Workflow'
        verbose_name_plural = 'Actions Workflow'
        indexes = [
            models.Index(fields=['action_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_action_type_display()})"
    
    @property
    def success_rate(self):
        """Taux de succès des actions"""
        if self.execution_count == 0:
            return 0
        return (self.success_count / self.execution_count) * 100
