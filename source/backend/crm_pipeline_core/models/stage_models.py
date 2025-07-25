# /var/www/megahub/backend/crm_pipeline_core/models/stage_models.py
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .base_models import PipelineBaseMixin

class Stage(PipelineBaseMixin):
    """Étape dans un pipeline commercial"""
    
    STAGE_TYPES = [
        ('open', 'Ouvert'),
        ('closed_won', 'Fermé Gagné'),
        ('closed_lost', 'Fermé Perdu'),
        ('on_hold', 'En Attente'),
        ('qualification', 'Qualification'),
        ('proposal', 'Proposition'),
        ('negotiation', 'Négociation'),
        ('decision', 'Décision'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pipeline = models.ForeignKey(
        'crm_pipeline_core.Pipeline',
        on_delete=models.CASCADE,
        related_name='stages',
        help_text="Pipeline parent"
    )
    name = models.CharField(
        max_length=100,
        help_text="Nom de l'étape"
    )
    
    # Position et type
    stage_type = models.CharField(
        max_length=20,
        choices=STAGE_TYPES,
        default='open',
        help_text="Type d'étape"
    )
    order = models.IntegerField(
        help_text="Ordre dans le pipeline"
    )
    
    # Probabilités et durées
    default_probability = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Probabilité par défaut (%)"
    )
    expected_duration_days = models.IntegerField(
        null=True,
        blank=True,
        help_text="Durée moyenne attendue (jours)"
    )
    
    # Statuts de fermeture
    is_closed_won = models.BooleanField(
        default=False,
        help_text="Étape de fermeture gagnée"
    )
    is_closed_lost = models.BooleanField(
        default=False,
        help_text="Étape de fermeture perdue"
    )
    
    # Configuration
    description = models.TextField(
        blank=True,
        help_text="Description de l'étape"
    )
    color_code = models.CharField(
        max_length=7,
        default='#6a5acd',
        help_text="Code couleur hex"
    )
    
    # Champs requis
    required_fields = models.JSONField(
        default=list,
        blank=True,
        help_text="Champs obligatoires pour cette étape"
    )
    
    # Actions automatiques - FIX RELATED_NAME
    auto_assign_to = models.ForeignKey(
        'users_core.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='auto_assigned_stages',  # ✅ FIX
        help_text="Assignation automatique"
    )
    
    # Notifications
    notify_on_entry = models.BooleanField(
        default=False,
        help_text="Notifier à l'entrée dans l'étape"
    )
    notify_on_stale = models.BooleanField(
        default=False,
        help_text="Notifier si stagnation"
    )
    stale_days_threshold = models.IntegerField(
        null=True,
        blank=True,
        help_text="Seuil de stagnation (jours)"
    )
    
    # Règles de progression
    can_skip = models.BooleanField(
        default=True,
        help_text="Peut être ignorée"
    )
    requires_approval = models.BooleanField(
        default=False,
        help_text="Nécessite approbation pour sortir"
    )
    approval_users = models.ManyToManyField(
        'users_core.CustomUser',
        blank=True,
        related_name='stage_approvals',
        help_text="Utilisateurs qui peuvent approuver"
    )
    
    # Métriques
    conversion_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Taux de conversion vers étape suivante (%)"
    )
    average_duration = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Durée moyenne réelle (jours)"
    )
    
    # Statut
    is_active = models.BooleanField(
        default=True,
        help_text="Étape active"
    )
    
    class Meta:
        db_table = 'crm_stage'
        unique_together = ['pipeline', 'order']
        ordering = ['pipeline', 'order']
        verbose_name = 'Étape Pipeline'
        verbose_name_plural = 'Étapes Pipeline'
        indexes = [
            models.Index(fields=['pipeline', 'order']),
            models.Index(fields=['stage_type']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_closed_won', 'is_closed_lost']),
        ]
    
    def __str__(self):
        return f"{self.pipeline.name} - {self.name} (#{self.order})"
    
    @property
    def is_closed_stage(self):
        """Vérifie si c'est une étape de fermeture"""
        return self.is_closed_won or self.is_closed_lost
    
    def get_next_stage(self):
        """Retourne l'étape suivante dans le pipeline"""
        return Stage.objects.filter(
            pipeline=self.pipeline,
            order__gt=self.order,
            is_active=True
        ).first()
    
    def get_previous_stage(self):
        """Retourne l'étape précédente dans le pipeline"""
        return Stage.objects.filter(
            pipeline=self.pipeline,
            order__lt=self.order,
            is_active=True
        ).last()
    
    def get_opportunities_count(self):
        """Nombre d'opportunités dans cette étape"""
        return self.opportunities.filter(is_closed=False).count()
    
    def get_opportunities_value(self):
        """Valeur totale des opportunités dans cette étape"""
        from django.db.models import Sum
        result = self.opportunities.filter(is_closed=False).aggregate(
            total=Sum('amount')
        )
        return result['total'] or 0
    
    def get_average_time_in_stage(self):
        """Temps moyen passé dans cette étape"""
        # À implémenter avec logique de calcul
        # basée sur l'historique des opportunités
        return self.average_duration
    
    def calculate_conversion_rate(self):
        """Recalcule le taux de conversion"""
        # Opportunités qui sont passées par cette étape
        total_opps = self.opportunities.count()
        if total_opps == 0:
            self.conversion_rate = 0
        else:
            # Opportunités qui ont progressé vers l'étape suivante
            next_stage = self.get_next_stage()
            if next_stage:
                progressed_opps = next_stage.opportunities.count()
                self.conversion_rate = (progressed_opps / total_opps) * 100
            else:
                # Dernière étape, compter les gagnées
                won_opps = self.opportunities.filter(is_won=True).count()
                self.conversion_rate = (won_opps / total_opps) * 100
        
        self.save(update_fields=['conversion_rate'])

class StageTransition(PipelineBaseMixin):
    """Historique des transitions entre étapes"""
    
    TRANSITION_TYPES = [
        ('forward', 'Progression'),
        ('backward', 'Régression'),
        ('skip', 'Saut d\'étape'),
        ('reset', 'Remise à zéro'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relations
    opportunity = models.ForeignKey(
        'crm_entities_core.Opportunity',
        on_delete=models.CASCADE,
        related_name='stage_transitions',
        help_text="Opportunité concernée"
    )
    from_stage = models.ForeignKey(
        'crm_pipeline_core.Stage',
        on_delete=models.CASCADE,
        related_name='transitions_from',
        null=True,
        blank=True,
        help_text="Étape source"
    )
    to_stage = models.ForeignKey(
        'crm_pipeline_core.Stage',
        on_delete=models.CASCADE,
        related_name='transitions_to',
        help_text="Étape destination"
    )
    
    # Détails de la transition
    transition_type = models.CharField(
        max_length=15,
        choices=TRANSITION_TYPES,
        help_text="Type de transition"
    )
    transition_date = models.DateTimeField(
        auto_now_add=True,
        help_text="Date de transition"
    )
    
    # Utilisateur et raison - FIX RELATED_NAME
    transitioned_by = models.ForeignKey(
        'users_core.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='performed_stage_transitions',  # ✅ FIX
        help_text="Utilisateur qui a effectué la transition"
    )
    reason = models.TextField(
        blank=True,
        help_text="Raison de la transition"
    )
    
    # Durée dans l'étape précédente
    duration_in_previous_stage = models.IntegerField(
        null=True,
        blank=True,
        help_text="Durée dans l'étape précédente (heures)"
    )
    
    # Approbation
    requires_approval = models.BooleanField(
        default=False,
        help_text="Transition nécessite approbation"
    )
    approved = models.BooleanField(
        default=True,
        help_text="Transition approuvée"
    )
    approved_by = models.ForeignKey(
        'users_core.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_stage_transitions',  # ✅ FIX
        help_text="Utilisateur qui a approuvé"
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date d'approbation"
    )
    
    class Meta:
        db_table = 'crm_stage_transition'
        ordering = ['-transition_date']
        verbose_name = 'Transition Étape'
        verbose_name_plural = 'Transitions Étapes'
        indexes = [
            models.Index(fields=['opportunity', 'transition_date']),
            models.Index(fields=['from_stage', 'to_stage']),
            models.Index(fields=['transition_type']),
            models.Index(fields=['approved']),
        ]
    
    def __str__(self):
        from_name = self.from_stage.name if self.from_stage else "Début"
        return f"{self.opportunity.name}: {from_name} → {self.to_stage.name}"
    
    def save(self, *args, **kwargs):
        # Calculer la durée dans l'étape précédente
        if self.from_stage and not self.duration_in_previous_stage:
            # Chercher la transition précédente
            previous_transition = StageTransition.objects.filter(
                opportunity=self.opportunity,
                to_stage=self.from_stage
            ).order_by('-transition_date').first()
            
            if previous_transition:
                duration = self.transition_date - previous_transition.transition_date
                self.duration_in_previous_stage = int(duration.total_seconds() / 3600)
        
        super().save(*args, **kwargs)
