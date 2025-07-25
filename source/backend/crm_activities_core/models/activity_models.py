# /var/www/megahub/backend/crm_activities_core/models/activity_models.py
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .base_models import ActivityBaseMixin

class Activity(ActivityBaseMixin):
    """Activité CRM de base - Modèle central unifié"""
    
    ACTIVITY_TYPES = [
        ('call', 'Appel'),
        ('email', 'Email'), 
        ('meeting', 'Réunion'),
        ('task', 'Tâche'),
        ('note', 'Note'),
        ('comment', 'Commentaire'),
        ('reminder', 'Rappel'),
        ('demo', 'Démonstration'),
        ('proposal', 'Proposition'),
        ('follow_up', 'Suivi'),
        ('other', 'Autre'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Faible'),
        ('medium', 'Moyenne'),
        ('high', 'Élevée'),
        ('urgent', 'Urgente'),
    ]
    
    STATUS_CHOICES = [
        ('planned', 'Planifié'),
        ('in_progress', 'En cours'),
        ('completed', 'Terminé'),
        ('cancelled', 'Annulé'),
        ('postponed', 'Reporté'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.CharField(
        max_length=255,
        help_text="Sujet de l'activité"
    )
    
    # Classification - CŒUR DU SYSTÈME
    activity_type = models.CharField(
        max_length=20,
        choices=ACTIVITY_TYPES,
        help_text="Type d'activité"
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_LEVELS,
        default='medium',
        help_text="Priorité"
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='planned',
        help_text="Statut"
    )
    
    # Contenu universel
    description = models.TextField(
        blank=True,
        help_text="Description détaillée"
    )
    location = models.CharField(
        max_length=255,
        blank=True,
        help_text="Lieu (réunions, appels)"
    )
    
    # Durée universelle
    duration_minutes = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        help_text="Durée en minutes"
    )
    
    # Participants universels
    participants = models.ManyToManyField(
        'users_core.CustomUser',
        through='ActivityParticipant',
        related_name='participated_activities',
        blank=True,
        help_text="Participants"
    )
    
    # Résultat universel
    outcome = models.TextField(
        blank=True,
        help_text="Résultat/Notes de l'activité"
    )
    satisfaction_score = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Score de satisfaction (1-5)"
    )
    
    # Suivi universel
    follow_up_required = models.BooleanField(
        default=False,
        help_text="Nécessite un suivi"
    )
    follow_up_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date de suivi"
    )
    follow_up_notes = models.TextField(
        blank=True,
        help_text="Notes pour le suivi"
    )
    
    # Automatisation universelle
    created_by_automation = models.BooleanField(
        default=False,
        help_text="Créé par automatisation"
    )
    automation_rule_id = models.UUIDField(
        null=True,
        blank=True,
        help_text="ID de la règle d'automatisation"
    )
    
    class Meta:
        db_table = 'crm_activity'
        ordering = ['-scheduled_date', '-created_at']
        verbose_name = 'Activité CRM'
        verbose_name_plural = 'Activités CRM'
        indexes = [
            models.Index(fields=['activity_type', 'status']),
            models.Index(fields=['priority', 'due_date']),
            models.Index(fields=['follow_up_required', 'follow_up_date']),
            models.Index(fields=['created_by_automation']),
        ]
    
    def __str__(self):
        return f"{self.get_activity_type_display()}: {self.subject}"
    
    @property
    def is_communication(self):
        """Vérifie si c'est une activité de communication"""
        return self.activity_type in ['call', 'email', 'meeting']
    
    @property
    def is_task_based(self):
        """Vérifie si c'est une activité basée tâches"""
        return self.activity_type in ['task', 'reminder']
    
    @property
    def is_note_based(self):
        """Vérifie si c'est une activité basée notes"""
        return self.activity_type in ['note', 'comment']
    
    def create_follow_up_activity(self):
        """Crée une activité de suivi"""
        if not self.follow_up_required or not self.follow_up_date:
            return None
        
        follow_up = Activity.objects.create(
            subject=f"Suivi: {self.subject}",
            activity_type='follow_up',
            description=self.follow_up_notes,
            scheduled_date=self.follow_up_date,
            assigned_to=self.assigned_to,
            brand=self.brand,
            owner=self.owner,
            related_content_type=self.related_content_type,
            related_object_id=self.related_object_id,
            priority=self.priority
        )
        return follow_up

class ActivityParticipant(models.Model):
    """Participants aux activités - Table de liaison universelle"""
    
    PARTICIPATION_STATUS = [
        ('invited', 'Invité'),
        ('accepted', 'Accepté'),
        ('declined', 'Décliné'),
        ('tentative', 'Incertain'),
        ('attended', 'Présent'),
        ('absent', 'Absent'),
    ]
    
    PARTICIPANT_ROLES = [
        ('organizer', 'Organisateur'),
        ('required', 'Requis'),
        ('optional', 'Optionnel'),
        ('observer', 'Observateur'),
    ]
    
    # Relations
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        help_text="Activité"
    )
    user = models.ForeignKey(
        'users_core.CustomUser',
        on_delete=models.CASCADE,
        help_text="Participant"
    )
    
    # Détails participation
    role = models.CharField(
        max_length=15,
        choices=PARTICIPANT_ROLES,
        default='required',
        help_text="Rôle"
    )
    status = models.CharField(
        max_length=15,
        choices=PARTICIPATION_STATUS,
        default='invited',
        help_text="Statut"
    )
    
    # Dates
    invited_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Invité le"
    )
    responded_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Réponse le"
    )
    
    # Notes
    notes = models.TextField(
        blank=True,
        help_text="Notes"
    )
    
    class Meta:
        db_table = 'crm_activity_participant'
        unique_together = ['activity', 'user']
        ordering = ['role', 'user__first_name']
        verbose_name = 'Participant Activité'
        verbose_name_plural = 'Participants Activités'
    
    def __str__(self):
        return f"{self.activity.subject} - {self.user.get_full_name()}"

class ActivityTemplate(ActivityBaseMixin):
    """Templates d'activités réutilisables"""
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=100,
        help_text="Nom du template"
    )
    
    # Template data
    template_data = models.JSONField(
        default=dict,
        help_text="Données du template"
    )
    
    # Configuration
    is_public = models.BooleanField(
        default=False,
        help_text="Template public"
    )
    usage_count = models.IntegerField(
        default=0,
        help_text="Utilisations"
    )
    
    # Catégorie
    category = models.CharField(
        max_length=50,
        blank=True,
        help_text="Catégorie"
    )
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="Tags"
    )
    
    class Meta:
        db_table = 'crm_activity_template'
        ordering = ['name']
        verbose_name = 'Template Activité'
        verbose_name_plural = 'Templates Activités'
    
    def __str__(self):
        return self.name
