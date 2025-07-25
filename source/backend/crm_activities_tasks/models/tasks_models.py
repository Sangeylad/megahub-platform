# /var/www/megahub/backend/crm_activities_tasks/models/tasks_models.py
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from crm_entities_core.models import CRMBaseMixin

class TaskActivity(CRMBaseMixin):
    """Extension pour activités de type tâche - OneToOne avec Activity"""
    
    TASK_CATEGORIES = [
        ('follow_up', 'Suivi'),
        ('research', 'Recherche'),
        ('preparation', 'Préparation'),
        ('data_entry', 'Saisie'),
        ('review', 'Revue'),
        ('approval', 'Approbation'),
        ('contact', 'Contact'),
        ('admin', 'Administratif'),
        ('other', 'Autre'),
    ]
    
    # Relation avec Activity de base
    activity = models.OneToOneField(
        'crm_activities_core.Activity',
        on_delete=models.CASCADE,
        related_name='task_details',
        help_text="Activité de base"
    )
    
    # Spécifique tâches
    task_category = models.CharField(
        max_length=20,
        choices=TASK_CATEGORIES,
        help_text="Catégorie de tâche"
    )
    instructions = models.TextField(
        blank=True,
        help_text="Instructions spécifiques"
    )
    
    # Progression
    progress_percentage = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="% d'avancement"
    )
    
    # Durée
    estimated_duration = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        help_text="Durée estimée (minutes)"
    )
    actual_duration = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Durée réelle (minutes)"
    )
    
    # Dépendances
    depends_on = models.ManyToManyField(
        'self',
        through='TaskDependency',
        symmetrical=False,
        related_name='blocks',
        blank=True,
        help_text="Dépend de ces tâches"
    )
    
    # Délégation
    delegated_to = models.ForeignKey(
        'users_core.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='delegated_tasks',
        help_text="Délégué à"
    )
    delegation_notes = models.TextField(
        blank=True,
        help_text="Notes de délégation"
    )
    
    # Récurrence
    is_recurring = models.BooleanField(
        default=False,
        help_text="Tâche récurrente"
    )
    recurrence_pattern = models.JSONField(
        default=dict,
        blank=True,
        help_text="Modèle récurrence"
    )
    parent_recurring_task = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='recurring_instances',
        help_text="Tâche récurrente parent"
    )
    
    # Résultat
    completion_notes = models.TextField(
        blank=True,
        help_text="Notes de completion"
    )
    deliverables = models.JSONField(
        default=list,
        blank=True,
        help_text="Livrables"
    )
    
    class Meta:
        db_table = 'crm_task_activity'
        verbose_name = 'Détails Tâche'
        verbose_name_plural = 'Détails Tâches'
        indexes = [
            models.Index(fields=['task_category']),
            models.Index(fields=['delegated_to']),
            models.Index(fields=['is_recurring']),
        ]
    
    def __str__(self):
        return f"Tâche - {self.activity.subject}"
    
    @property
    def can_start(self):
        """Peut être démarrée (dépendances OK)"""
        return not self.depends_on.filter(
            activity__status__in=['planned', 'in_progress']
        ).exists()

class TaskDependency(models.Model):
    """Dépendances entre tâches"""
    
    DEPENDENCY_TYPES = [
        ('finish_to_start', 'Fin à Début'),
        ('start_to_start', 'Début à Début'),
        ('finish_to_finish', 'Fin à Fin'),
        ('start_to_finish', 'Début à Fin'),
    ]
    
    # Relations
    predecessor = models.ForeignKey(
        TaskActivity,
        on_delete=models.CASCADE,
        related_name='successor_dependencies',
        help_text="Tâche prédécesseur"
    )
    successor = models.ForeignKey(
        TaskActivity,
        on_delete=models.CASCADE,
        related_name='predecessor_dependencies',
        help_text="Tâche successeur"
    )
    
    # Configuration
    dependency_type = models.CharField(
        max_length=20,
        choices=DEPENDENCY_TYPES,
        default='finish_to_start',
        help_text="Type dépendance"
    )
    lag_days = models.IntegerField(
        default=0,
        help_text="Délai (jours)"
    )
    notes = models.TextField(
        blank=True,
        help_text="Notes"
    )
    
    class Meta:
        db_table = 'crm_task_dependency'
        unique_together = ['predecessor', 'successor']
        verbose_name = 'Dépendance Tâche'
        verbose_name_plural = 'Dépendances Tâches'
    
    def __str__(self):
        return f"{self.predecessor.activity.subject} → {self.successor.activity.subject}"

class ReminderActivity(CRMBaseMixin):
    """Extension pour activités de rappel - OneToOne avec Activity"""
    
    FREQUENCY_CHOICES = [
        ('once', 'Une fois'),
        ('daily', 'Quotidien'),
        ('weekly', 'Hebdomadaire'),
        ('monthly', 'Mensuel'),
        ('quarterly', 'Trimestriel'),
        ('yearly', 'Annuel'),
    ]
    
    # Relation avec Activity de base
    activity = models.OneToOneField(
        'crm_activities_core.Activity',
        on_delete=models.CASCADE,
        related_name='reminder_details',
        help_text="Activité de base"
    )
    
    # Configuration rappel
    reminder_date = models.DateTimeField(help_text="Date du rappel")
    advance_notice_minutes = models.IntegerField(
        default=15,
        help_text="Préavis (minutes)"
    )
    
    # Récurrence
    frequency = models.CharField(
        max_length=15,
        choices=FREQUENCY_CHOICES,
        default='once',
        help_text="Fréquence"
    )
    end_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date fin récurrence"
    )
    max_occurrences = models.IntegerField(
        null=True,
        blank=True,
        help_text="Max occurrences"
    )
    
    # Notifications
    notification_methods = models.JSONField(
        default=list,
        help_text="Méthodes de notification"
    )
    
    # Statut envoi
    is_sent = models.BooleanField(default=False, help_text="Envoyé")
    sent_date = models.DateTimeField(null=True, blank=True, help_text="Date envoi")
    is_acknowledged = models.BooleanField(default=False, help_text="Accusé réception")
    acknowledged_date = models.DateTimeField(null=True, blank=True, help_text="Date accusé")
    
    # Relation optionnelle vers une tâche
    related_task = models.ForeignKey(
        TaskActivity,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='reminders',
        help_text="Tâche associée"
    )
    
    class Meta:
        db_table = 'crm_reminder_activity'
        verbose_name = 'Détails Rappel'
        verbose_name_plural = 'Détails Rappels'
        indexes = [
            models.Index(fields=['reminder_date', 'is_sent']),
            models.Index(fields=['frequency']),
            models.Index(fields=['related_task']),
        ]
    
    def __str__(self):
        return f"Rappel - {self.activity.subject}"
