# /var/www/megahub/backend/crm_entities_scoring/models/scoring_models.py
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from crm_entities_core.models import CRMBaseMixin

class EntityScore(CRMBaseMixin):
    """Scoring des entités CRM (Account, Contact, Opportunity)"""
    
    ENTITY_TYPES = [
        ('account', 'Compte'),
        ('contact', 'Contact'),
        ('opportunity', 'Opportunité'),
    ]
    
    SCORE_TYPES = [
        ('health', 'Score Santé'),
        ('engagement', 'Score Engagement'),
        ('propensity', 'Propension Achat'),
        ('churn_risk', 'Risque Churn'),
        ('lead_quality', 'Qualité Lead'),
        ('upsell_potential', 'Potentiel Upsell'),
        ('influence', 'Score Influence'),
        ('decision_power', 'Pouvoir Décision'),
    ]
    
    CALCULATION_METHODS = [
        ('manual', 'Manuel'),
        ('rule_based', 'Règles Métier'),
        ('ml_model', 'Modèle ML'),
        ('weighted_average', 'Moyenne Pondérée'),
        ('composite', 'Score Composite'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Entité scorée (Generic Foreign Key pattern)
    entity_type = models.CharField(
        max_length=15,
        choices=ENTITY_TYPES,
        help_text="Type d'entité scorée"
    )
    entity_id = models.UUIDField(
        help_text="ID de l'entité scorée"
    )
    
    # Type et valeur du score
    score_type = models.CharField(
        max_length=20,
        choices=SCORE_TYPES,
        help_text="Type de score"
    )
    score_value = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Valeur du score (0-100)"
    )
    
    # Méthodologie
    calculation_method = models.CharField(
        max_length=20,
        choices=CALCULATION_METHODS,
        help_text="Méthode de calcul"
    )
    model_version = models.CharField(
        max_length=20,
        blank=True,
        help_text="Version du modèle (si ML)"
    )
    
    # Détails du calcul
    calculation_details = models.JSONField(
        default=dict,
        blank=True,
        help_text="Détails du calcul en JSON"
    )
    confidence_level = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Niveau de confiance (0-1)"
    )
    
    # Historique
    previous_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Score précédent"
    )
    score_change = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Variation du score"
    )
    
    # Dates
    calculated_at = models.DateTimeField(
        auto_now=True,
        help_text="Date de calcul"
    )
    valid_until = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Validité du score"
    )
    
    # Alertes
    requires_attention = models.BooleanField(
        default=False,
        help_text="Score nécessite attention"
    )
    alert_threshold_reached = models.BooleanField(
        default=False,
        help_text="Seuil d'alerte atteint"
    )
    
    class Meta:
        db_table = 'crm_entity_score'
        unique_together = ['entity_type', 'entity_id', 'score_type']
        ordering = ['-calculated_at']
        verbose_name = 'Score Entité'
        verbose_name_plural = 'Scores Entités'
        indexes = [
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['score_type', 'score_value']),
            models.Index(fields=['brand', 'requires_attention']),
            models.Index(fields=['calculated_at']),
        ]
    
    def __str__(self):
        return f"{self.get_entity_type_display()} {self.entity_id} - {self.get_score_type_display()}: {self.score_value}"
    
    def save(self, *args, **kwargs):
        # Calculer la variation si score précédent existe
        if self.pk and self.previous_score is not None:
            self.score_change = self.score_value - self.previous_score
        
        # Vérifier les seuils d'alerte selon le type de score
        self.check_alert_thresholds()
        
        super().save(*args, **kwargs)
    
    def check_alert_thresholds(self):
        """Vérifie si les seuils d'alerte sont atteints"""
        alert_thresholds = {
            'health': 30,  # Score santé < 30%
            'churn_risk': 70,  # Risque churn > 70%
            'engagement': 25,  # Engagement < 25%
        }
        
        threshold = alert_thresholds.get(self.score_type)
        if threshold:
            if self.score_type == 'churn_risk':
                self.alert_threshold_reached = float(self.score_value) > threshold
            else:
                self.alert_threshold_reached = float(self.score_value) < threshold
            
            self.requires_attention = self.alert_threshold_reached

class ScoreHistory(CRMBaseMixin):
    """Historique des évolutions de scores"""
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relation vers le score principal
    entity_score = models.ForeignKey(
        EntityScore,
        on_delete=models.CASCADE,
        related_name='history',
        help_text="Score principal"
    )
    
    # Valeurs historiques
    old_value = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Ancienne valeur"
    )
    new_value = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Nouvelle valeur"
    )
    change_amount = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text="Montant du changement"
    )
    change_percentage = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text="Pourcentage de changement"
    )
    
    # Cause du changement
    change_reason = models.CharField(
        max_length=100,
        blank=True,
        help_text="Raison du changement"
    )
    triggered_by = models.CharField(
        max_length=50,
        blank=True,
        help_text="Déclenché par (système, utilisateur, etc.)"
    )
    
    # Métadonnées
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Métadonnées du changement"
    )
    
    class Meta:
        db_table = 'crm_score_history'
        ordering = ['-created_at']
        verbose_name = 'Historique Score'
        verbose_name_plural = 'Historiques Scores'
        indexes = [
            models.Index(fields=['entity_score', 'created_at']),
            models.Index(fields=['change_percentage']),
        ]
    
    def __str__(self):
        return f"{self.entity_score.get_score_type_display()}: {self.old_value} → {self.new_value}"
    
    def save(self, *args, **kwargs):
        # Calculer automatiquement les changements
        self.change_amount = self.new_value - self.old_value
        if self.old_value != 0:
            self.change_percentage = (self.change_amount / self.old_value) * 100
        else:
            self.change_percentage = 100 if self.new_value > 0 else 0
        
        super().save(*args, **kwargs)

class ScoreRule(CRMBaseMixin):
    """Règles de calcul des scores"""
    
    RULE_TYPES = [
        ('threshold', 'Seuil'),
        ('formula', 'Formule'),
        ('condition', 'Condition'),
        ('weight', 'Pondération'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Règle
    name = models.CharField(
        max_length=100,
        help_text="Nom de la règle"
    )
    score_type = models.CharField(
        max_length=20,
        choices=EntityScore.SCORE_TYPES,
        help_text="Type de score concerné"
    )
    rule_type = models.CharField(
        max_length=15,
        choices=RULE_TYPES,
        help_text="Type de règle"
    )
    
    # Définition
    condition = models.TextField(
        help_text="Condition/formule de la règle"
    )
    weight = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=1.0,
        help_text="Poids de la règle"
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
    
    # Applicabilité
    entity_types = models.JSONField(
        default=list,
        help_text="Types d'entités concernés"
    )
    
    class Meta:
        db_table = 'crm_score_rule'
        ordering = ['priority', 'name']
        verbose_name = 'Règle Score'
        verbose_name_plural = 'Règles Scores'
        indexes = [
            models.Index(fields=['score_type', 'is_active']),
            models.Index(fields=['priority']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_score_type_display()})"
