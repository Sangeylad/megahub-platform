# /var/www/megahub/backend/crm_analytics_predictions/models/predictions_models.py
import uuid
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.validators import MinValueValidator, MaxValueValidator
from crm_analytics_core.models import AnalyticsBaseMixin

class Prediction(AnalyticsBaseMixin):
    """Prédiction IA pour les entités CRM"""
    
    PREDICTION_TYPES = [
        ('churn_risk', 'Risque de Churn'),
        ('lifetime_value', 'Lifetime Value'),
        ('conversion_probability', 'Probabilité de Conversion'),
        ('next_best_action', 'Meilleure Action Suivante'),
        ('optimal_pricing', 'Prix Optimal'),
        ('lead_scoring', 'Score de Lead'),
        ('upsell_opportunity', 'Opportunité Upsell'),
        ('renewal_likelihood', 'Probabilité Renouvellement'),
        ('engagement_score', 'Score d\'Engagement'),
        ('custom', 'Personnalisé'),
    ]
    
    MODEL_TYPES = [
        ('logistic_regression', 'Régression Logistique'),
        ('random_forest', 'Random Forest'),
        ('gradient_boosting', 'Gradient Boosting'),
        ('neural_network', 'Réseau de Neurones'),
        ('svm', 'SVM'),
        ('naive_bayes', 'Naive Bayes'),
        ('ensemble', 'Ensemble'),
        ('deep_learning', 'Deep Learning'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=100,
        help_text="Nom de la prédiction"
    )
    
    # Classification
    prediction_type = models.CharField(
        max_length=25,
        choices=PREDICTION_TYPES,
        help_text="Type de prédiction"
    )
    model_type = models.CharField(
        max_length=20,
        choices=MODEL_TYPES,
        help_text="Type de modèle ML"
    )
    
    # Entité cible
    target_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        help_text="Type d'entité cible"
    )
    target_object_id = models.UUIDField(
        help_text="ID de l'entité cible"
    )
    target_object = GenericForeignKey('target_content_type', 'target_object_id')
    
    # Résultat de prédiction
    predicted_value = models.DecimalField(
        max_digits=15,
        decimal_places=6,
        help_text="Valeur prédite"
    )
    confidence_score = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Score de confiance (0-1)"
    )
    probability_distribution = models.JSONField(
        default=dict,
        blank=True,
        help_text="Distribution de probabilité"
    )
    
    # Facteurs influents
    feature_importance = models.JSONField(
        default=dict,
        help_text="Importance des features"
    )
    contributing_factors = models.JSONField(
        default=list,
        help_text="Facteurs contributifs"
    )
    
    # Modèle utilisé
    model_version = models.CharField(
        max_length=20,
        help_text="Version du modèle"
    )
    model_accuracy = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Précision du modèle"
    )
    training_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date d'entraînement du modèle"
    )
    
    # Recommandations
    recommended_actions = models.JSONField(
        default=list,
        blank=True,
        help_text="Actions recommandées"
    )
    next_review_date = models.DateField(
        null=True,
        blank=True,
        help_text="Prochaine révision"
    )
    
    # Validation
    actual_outcome = models.DecimalField(
        max_digits=15,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Résultat réel (pour validation)"
    )
    prediction_accuracy = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Précision de cette prédiction"
    )
    
    # État
    is_active = models.BooleanField(
        default=True,
        help_text="Prédiction active"
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date d'expiration"
    )
    
    class Meta:
        db_table = 'crm_analytics_prediction'
        ordering = ['-created_at']
        verbose_name = 'Prédiction Analytics'
        verbose_name_plural = 'Prédictions Analytics'
        indexes = [
            models.Index(fields=['prediction_type', 'model_type']),
            models.Index(fields=['target_content_type', 'target_object_id']),
            models.Index(fields=['confidence_score']),
            models.Index(fields=['expires_at', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.get_prediction_type_display()} - {self.target_object}"
    
    @property
    def is_expired(self):
        """Vérifie si la prédiction est expirée"""
        from django.utils import timezone
        return self.expires_at and self.expires_at < timezone.now()
    
    @property
    def confidence_level(self):
        """Niveau de confiance textuel"""
        score = float(self.confidence_score)
        if score >= 0.9:
            return 'très_élevé'
        elif score >= 0.75:
            return 'élevé'
        elif score >= 0.6:
            return 'moyen'
        elif score >= 0.4:
            return 'faible'
        else:
            return 'très_faible'

class Recommendation(AnalyticsBaseMixin):
    """Recommandation basée sur l'IA"""
    
    RECOMMENDATION_TYPES = [
        ('action', 'Action'),
        ('content', 'Contenu'),
        ('timing', 'Timing'),
        ('channel', 'Canal'),
        ('pricing', 'Pricing'),
        ('product', 'Produit'),
        ('personalization', 'Personnalisation'),
        ('optimization', 'Optimisation'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Faible'),
        ('medium', 'Moyenne'),
        ('high', 'Élevée'),
        ('urgent', 'Urgente'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(
        max_length=200,
        help_text="Titre de la recommandation"
    )
    
    # Classification
    recommendation_type = models.CharField(
        max_length=20,
        choices=RECOMMENDATION_TYPES,
        help_text="Type de recommandation"
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_LEVELS,
        default='medium',
        help_text="Niveau de priorité"
    )
    
    # Entité cible
    target_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        help_text="Type d'entité cible"
    )
    target_object_id = models.UUIDField(
        help_text="ID de l'entité cible"
    )
    target_object = GenericForeignKey('target_content_type', 'target_object_id')
    
    # Contenu
    description = models.TextField(
        help_text="Description de la recommandation"
    )
    rationale = models.TextField(
        help_text="Justification de la recommandation"
    )
    expected_impact = models.TextField(
        blank=True,
        help_text="Impact attendu"
    )
    
    # Configuration
    action_items = models.JSONField(
        default=list,
        help_text="Actions à effectuer"
    )
    success_metrics = models.JSONField(
        default=list,
        blank=True,
        help_text="Métriques de succès"
    )
    
    # Scoring
    confidence_score = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Score de confiance"
    )
    expected_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Valeur attendue (€)"
    )
    effort_estimate = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Faible'),
            ('medium', 'Moyen'),
            ('high', 'Élevé'),
        ],
        blank=True,
        help_text="Estimation de l'effort"
    )
    
    # État et suivi
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'En attente'),
            ('accepted', 'Accepté'),
            ('rejected', 'Rejeté'),
            ('in_progress', 'En cours'),
            ('completed', 'Terminé'),
            ('expired', 'Expiré'),
        ],
        default='pending',
        help_text="Statut de la recommandation"
    )
    
    # Dates
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date d'expiration"
    )
    accepted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date d'acceptation"
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date de completion"
    )
    
    # Assignation
    assigned_to = models.ForeignKey(
        'users_core.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_recommendations',
        help_text="Assigné à"
    )
    
    # Feedback
    feedback_rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Évaluation (1-5)"
    )
    feedback_comments = models.TextField(
        blank=True,
        help_text="Commentaires"
    )
    
    class Meta:
        db_table = 'crm_analytics_recommendation'
        ordering = ['-priority', '-confidence_score', '-created_at']
        verbose_name = 'Recommandation Analytics'
        verbose_name_plural = 'Recommandations Analytics'
        indexes = [
            models.Index(fields=['recommendation_type', 'priority']),
            models.Index(fields=['target_content_type', 'target_object_id']),
            models.Index(fields=['status', 'expires_at']),
            models.Index(fields=['assigned_to', 'status']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_priority_display()})"

class Insight(AnalyticsBaseMixin):
    """Insight généré par l'IA"""
    
    INSIGHT_TYPES = [
        ('pattern', 'Motif Détecté'),
        ('anomaly', 'Anomalie'),
        ('opportunity', 'Opportunité'),
        ('risk', 'Risque'),
        ('correlation', 'Corrélation'),
        ('trend', 'Tendance'),
        ('seasonal', 'Saisonnier'),
        ('performance', 'Performance'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(
        max_length=200,
        help_text="Titre de l'insight"
    )
    
    # Classification
    insight_type = models.CharField(
        max_length=15,
        choices=INSIGHT_TYPES,
        help_text="Type d'insight"
    )
    category = models.CharField(
        max_length=50,
        blank=True,
        help_text="Catégorie"
    )
    
    # Contenu
    summary = models.TextField(
        help_text="Résumé de l'insight"
    )
    detailed_analysis = models.TextField(
        blank=True,
        help_text="Analyse détaillée"
    )
    
    # Données supportant l'insight
    supporting_data = models.JSONField(
        default=dict,
        help_text="Données supportant l'insight"
    )
    statistical_significance = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Significativité statistique"
    )
    
    # Impact
    impact_level = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Faible'),
            ('medium', 'Moyen'),
            ('high', 'Élevé'),
            ('critical', 'Critique'),
        ],
        default='medium',
        help_text="Niveau d'impact"
    )
    affected_entities = models.JSONField(
        default=list,
        help_text="Entités affectées"
    )
    
    # Recommandations associées
    recommendations = models.ManyToManyField(
        Recommendation,
        related_name='insights',
        blank=True,
        help_text="Recommandations liées"
    )
    
    # Validation
    is_validated = models.BooleanField(
        default=False,
        help_text="Insight validé"
    )
    validated_by = models.ForeignKey(
        'users_core.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='validated_insights',
        help_text="Validé par"
    )
    validated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date de validation"
    )
    
    # État
    is_active = models.BooleanField(
        default=True,
        help_text="Insight actif"
    )
    is_actionable = models.BooleanField(
        default=True,
        help_text="Insight actionnable"
    )
    
    class Meta:
        db_table = 'crm_analytics_insight'
        ordering = ['-impact_level', '-created_at']
        verbose_name = 'Insight Analytics'
        verbose_name_plural = 'Insights Analytics'
        indexes = [
            models.Index(fields=['insight_type', 'category']),
            models.Index(fields=['impact_level', 'is_active']),
            models.Index(fields=['is_validated', 'validated_at']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_insight_type_display()})"
