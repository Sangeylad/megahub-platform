# /var/www/megahub/backend/crm_analytics_forecasting/models/forecasting_models.py
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from crm_analytics_core.models import AnalyticsBaseMixin

class Forecast(AnalyticsBaseMixin):
    """Prévision analytique CRM"""
    
    FORECAST_TYPES = [
        ('revenue', 'Revenus'),
        ('sales_volume', 'Volume de Ventes'),
        ('pipeline', 'Pipeline'),
        ('churn', 'Churn'),
        ('growth', 'Croissance'),
        ('seasonality', 'Saisonnalité'),
        ('demand', 'Demande'),
        ('custom', 'Personnalisé'),
    ]
    
    FORECAST_METHODS = [
        ('linear_regression', 'Régression Linéaire'),
        ('polynomial', 'Polynomiale'),
        ('exponential', 'Exponentielle'),
        ('arima', 'ARIMA'),
        ('prophet', 'Prophet'),
        ('machine_learning', 'Machine Learning'),
        ('weighted_average', 'Moyenne Pondérée'),
        ('seasonal_decomposition', 'Décomposition Saisonnière'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=100,
        help_text="Nom de la prévision"
    )
    
    # Classification
    forecast_type = models.CharField(
        max_length=20,
        choices=FORECAST_TYPES,
        help_text="Type de prévision"
    )
    forecast_method = models.CharField(
        max_length=25,
        choices=FORECAST_METHODS,
        help_text="Méthode de prévision"
    )
    
    # Configuration
    target_metric = models.CharField(
        max_length=100,
        help_text="Métrique cible"
    )
    horizon_days = models.IntegerField(
        help_text="Horizon de prévision (jours)"
    )
    confidence_interval = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=95.0,
        help_text="Intervalle de confiance (%)"
    )
    
    # Données historiques
    training_period_days = models.IntegerField(
        help_text="Période d'entraînement (jours)"
    )
    historical_data = models.JSONField(
        default=list,
        blank=True,
        help_text="Données historiques"
    )
    
    # Paramètres du modèle
    model_parameters = models.JSONField(
        default=dict,
        help_text="Paramètres du modèle"
    )
    seasonal_patterns = models.JSONField(
        default=dict,
        blank=True,
        help_text="Motifs saisonniers"
    )
    
    # Résultats
    predicted_values = models.JSONField(
        default=list,
        blank=True,
        help_text="Valeurs prédites"
    )
    confidence_bounds = models.JSONField(
        default=dict,
        blank=True,
        help_text="Bornes de confiance"
    )
    
    # Qualité
    accuracy_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Score de précision (%)"
    )
    mean_absolute_error = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Erreur absolue moyenne"
    )
    r_squared = models.DecimalField(
        max_digits=4,
        decimal_places=3,
        null=True,
        blank=True,
        help_text="Coefficient de détermination R²"
    )
    
    # État
    is_active = models.BooleanField(
        default=True,
        help_text="Prévision active"
    )
    last_trained_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Dernier entraînement"
    )
    
    class Meta:
        db_table = 'crm_analytics_forecast'
        ordering = ['-last_trained_at']
        verbose_name = 'Prévision Analytics'
        verbose_name_plural = 'Prévisions Analytics'
        indexes = [
            models.Index(fields=['forecast_type', 'forecast_method']),
            models.Index(fields=['target_metric']),
            models.Index(fields=['is_active', 'last_trained_at']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_forecast_type_display()})"

class ForecastScenario(AnalyticsBaseMixin):
    """Scénario de prévision"""
    
    SCENARIO_TYPES = [
        ('optimistic', 'Optimiste'),
        ('realistic', 'Réaliste'),
        ('pessimistic', 'Pessimiste'),
        ('best_case', 'Meilleur Cas'),
        ('worst_case', 'Pire Cas'),
        ('custom', 'Personnalisé'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    forecast = models.ForeignKey(
        Forecast,
        on_delete=models.CASCADE,
        related_name='scenarios',
        help_text="Prévision parent"
    )
    name = models.CharField(
        max_length=100,
        help_text="Nom du scénario"
    )
    
    # Classification
    scenario_type = models.CharField(
        max_length=15,
        choices=SCENARIO_TYPES,
        help_text="Type de scénario"
    )
    
    # Configuration
    assumptions = models.JSONField(
        default=dict,
        help_text="Hypothèses du scénario"
    )
    adjustments = models.JSONField(
        default=dict,
        blank=True,
        help_text="Ajustements appliqués"
    )
    probability = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Probabilité de réalisation (%)"
    )
    
    # Résultats
    predicted_values = models.JSONField(
        default=list,
        help_text="Valeurs prédites pour ce scénario"
    )
    impact_analysis = models.JSONField(
        default=dict,
        blank=True,
        help_text="Analyse d'impact"
    )
    
    # Métadonnées
    description = models.TextField(
        blank=True,
        help_text="Description du scénario"
    )
    
    class Meta:
        db_table = 'crm_forecast_scenario'
        unique_together = ['forecast', 'name']
        ordering = ['scenario_type', 'name']
        verbose_name = 'Scénario Prévision'
        verbose_name_plural = 'Scénarios Prévision'
    
    def __str__(self):
        return f"{self.forecast.name} - {self.name}"

class Trend(AnalyticsBaseMixin):
    """Tendance détectée dans les données"""
    
    TREND_DIRECTIONS = [
        ('up', 'Hausse'),
        ('down', 'Baisse'),
        ('stable', 'Stable'),
        ('volatile', 'Volatile'),
        ('seasonal', 'Saisonnier'),
    ]
    
    TREND_STRENGTHS = [
        ('weak', 'Faible'),
        ('moderate', 'Modérée'),
        ('strong', 'Forte'),
        ('very_strong', 'Très Forte'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=100,
        help_text="Nom de la tendance"
    )
    
    # Classification
    direction = models.CharField(
        max_length=15,
        choices=TREND_DIRECTIONS,
        help_text="Direction de la tendance"
    )
    strength = models.CharField(
        max_length=15,
        choices=TREND_STRENGTHS,
        help_text="Force de la tendance"
    )
    
    # Métriques
    metric_name = models.CharField(
        max_length=100,
        help_text="Nom de la métrique"
    )
    slope = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        help_text="Pente de la tendance"
    )
    correlation_coefficient = models.DecimalField(
        max_digits=4,
        decimal_places=3,
        validators=[MinValueValidator(-1), MaxValueValidator(1)],
        help_text="Coefficient de corrélation"
    )
    
    # Période
    detection_date = models.DateField(
        help_text="Date de détection"
    )
    trend_start_date = models.DateField(
        help_text="Début de la tendance"
    )
    trend_end_date = models.DateField(
        null=True,
        blank=True,
        help_text="Fin de la tendance (si applicable)"
    )
    
    # Contexte
    context_factors = models.JSONField(
        default=list,
        blank=True,
        help_text="Facteurs contextuels"
    )
    statistical_significance = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        null=True,
        blank=True,
        help_text="Significativité statistique"
    )
    
    # État
    is_active = models.BooleanField(
        default=True,
        help_text="Tendance active"
    )
    is_anomaly = models.BooleanField(
        default=False,
        help_text="Tendance anormale"
    )
    
    class Meta:
        db_table = 'crm_analytics_trend'
        ordering = ['-detection_date']
        verbose_name = 'Tendance Analytics'
        verbose_name_plural = 'Tendances Analytics'
        indexes = [
            models.Index(fields=['metric_name', 'direction']),
            models.Index(fields=['detection_date']),
            models.Index(fields=['is_active', 'is_anomaly']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.get_direction_display()} ({self.get_strength_display()})"
