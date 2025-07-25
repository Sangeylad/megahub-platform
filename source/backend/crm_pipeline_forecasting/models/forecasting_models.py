# /var/www/megahub/backend/crm_pipeline_forecasting/models/forecasting_models.py
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from crm_entities_core.models import CRMBaseMixin

class PipelineForecast(CRMBaseMixin):
    """Prévisions de pipeline commercial"""
    
    FORECAST_TYPES = [
        ('monthly', 'Mensuel'),
        ('quarterly', 'Trimestriel'),
        ('annual', 'Annuel'),
        ('custom', 'Personnalisé'),
    ]
    
    CALCULATION_METHODS = [
        ('probability_based', 'Basé sur probabilité'),
        ('historical_average', 'Moyenne historique'),
        ('linear_regression', 'Régression linéaire'),
        ('ml_model', 'Modèle ML'),
        ('manual', 'Manuel'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=100,
        help_text="Nom de la prévision"
    )
    
    # Scope
    pipeline = models.ForeignKey(
        'crm_pipeline_core.Pipeline',
        on_delete=models.CASCADE,
        related_name='forecasts',
        help_text="Pipeline concerné"
    )
    
    # Période
    forecast_type = models.CharField(
        max_length=15,
        choices=FORECAST_TYPES,
        help_text="Type de prévision"
    )
    start_date = models.DateField(
        help_text="Date de début"
    )
    end_date = models.DateField(
        help_text="Date de fin"
    )
    
    # Méthode de calcul
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
    
    # Prévisions
    target_revenue = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Objectif de revenus (€)"
    )
    forecasted_revenue = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Revenus prévus (€)"
    )
    actual_revenue = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Revenus réels (€)"
    )
    
    # Métriques additionnelles
    forecasted_deals = models.IntegerField(
        help_text="Nombre d'affaires prévues"
    )
    actual_deals = models.IntegerField(
        null=True,
        blank=True,
        help_text="Nombre d'affaires réelles"
    )
    
    # Confiance et précision
    confidence_score = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Score de confiance (0-1)"
    )
    accuracy_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Score de précision (%)"
    )
    
    # Détails du calcul
    calculation_details = models.JSONField(
        default=dict,
        help_text="Détails du calcul"
    )
    assumptions = models.TextField(
        blank=True,
        help_text="Hypothèses de la prévision"
    )
    
    # Statut
    is_published = models.BooleanField(
        default=False,
        help_text="Prévision publiée"
    )
    is_locked = models.BooleanField(
        default=False,
        help_text="Prévision verrouillée"
    )
    
    class Meta:
        db_table = 'crm_pipeline_forecast'
        unique_together = ['pipeline', 'start_date', 'end_date', 'forecast_type']
        ordering = ['-start_date']
        verbose_name = 'Prévision Pipeline'
        verbose_name_plural = 'Prévisions Pipeline'
        indexes = [
            models.Index(fields=['pipeline', 'start_date']),
            models.Index(fields=['forecast_type', 'is_published']),
            models.Index(fields=['end_date']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.start_date} à {self.end_date}"
    
    @property
    def variance_percentage(self):
        """Variance entre prévision et réalité en %"""
        if self.actual_revenue and self.forecasted_revenue:
            variance = self.actual_revenue - self.forecasted_revenue
            return (variance / self.forecasted_revenue) * 100
        return None
    
    @property
    def achievement_rate(self):
        """Taux de réalisation vs objectif en %"""
        if self.actual_revenue and self.target_revenue:
            return (self.actual_revenue / self.target_revenue) * 100
        return None
    
    def calculate_accuracy(self):
        """Calcule la précision de la prévision"""
        if self.actual_revenue and self.forecasted_revenue:
            error = abs(self.actual_revenue - self.forecasted_revenue)
            if self.forecasted_revenue > 0:
                accuracy = 100 - ((error / self.forecasted_revenue) * 100)
                self.accuracy_score = max(0, accuracy)
                self.save(update_fields=['accuracy_score'])

class ForecastSnapshot(CRMBaseMixin):
    """Instantanés de prévisions à un moment donné"""
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    forecast = models.ForeignKey(
        PipelineForecast,
        on_delete=models.CASCADE,
        related_name='snapshots',
        help_text="Prévision parent"
    )
    
    # Moment de l'instantané
    snapshot_date = models.DateTimeField(
        auto_now_add=True,
        help_text="Date de l'instantané"
    )
    
    # Données de l'instantané
    snapshot_data = models.JSONField(
        default=dict,
        help_text="Données complètes de la prévision"
    )
    
    # Métriques au moment de l'instantané
    total_pipeline_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Valeur totale du pipeline"
    )
    weighted_pipeline_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Valeur pondérée du pipeline"
    )
    opportunities_count = models.IntegerField(
        help_text="Nombre d'opportunités"
    )
    
    # Contexte
    triggered_by = models.CharField(
        max_length=50,
        help_text="Déclencheur de l'instantané"
    )
    notes = models.TextField(
        blank=True,
        help_text="Notes sur l'instantané"
    )
    
    class Meta:
        db_table = 'crm_forecast_snapshot'
        ordering = ['-snapshot_date']
        verbose_name = 'Instantané Prévision'
        verbose_name_plural = 'Instantanés Prévisions'
        indexes = [
            models.Index(fields=['forecast', 'snapshot_date']),
            models.Index(fields=['triggered_by']),
        ]
    
    def __str__(self):
        return f"{self.forecast.name} - {self.snapshot_date.strftime('%d/%m/%Y %H:%M')}"

class ForecastMetric(CRMBaseMixin):
    """Métriques détaillées des prévisions"""
    
    METRIC_TYPES = [
        ('revenue', 'Revenus'),
        ('deals_count', 'Nombre d\'affaires'),
        ('conversion_rate', 'Taux de conversion'),
        ('average_deal_size', 'Taille moyenne affaire'),
        ('sales_cycle', 'Cycle de vente'),
        ('win_rate', 'Taux de gain'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    forecast = models.ForeignKey(
        PipelineForecast,
        on_delete=models.CASCADE,
        related_name='metrics',
        help_text="Prévision parent"
    )
    
    # Métrique
    metric_type = models.CharField(
        max_length=20,
        choices=METRIC_TYPES,
        help_text="Type de métrique"
    )
    metric_name = models.CharField(
        max_length=100,
        help_text="Nom de la métrique"
    )
    
    # Valeurs
    target_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Valeur cible"
    )
    forecasted_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Valeur prévue"
    )
    actual_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Valeur réelle"
    )
    
    # Unité et format
    unit = models.CharField(
        max_length=20,
        default='',
        help_text="Unité de mesure"
    )
    is_percentage = models.BooleanField(
        default=False,
        help_text="Métrique en pourcentage"
    )
    
    class Meta:
        db_table = 'crm_forecast_metric'
        unique_together = ['forecast', 'metric_type']
        ordering = ['metric_name']
        verbose_name = 'Métrique Prévision'
        verbose_name_plural = 'Métriques Prévisions'
        indexes = [
            models.Index(fields=['forecast', 'metric_type']),
        ]
    
    def __str__(self):
        return f"{self.forecast.name} - {self.metric_name}"
    
    @property
    def variance_percentage(self):
        """Variance entre prévision et réalité"""
        if self.actual_value and self.forecasted_value:
            variance = self.actual_value - self.forecasted_value
            return (variance / self.forecasted_value) * 100
        return None
