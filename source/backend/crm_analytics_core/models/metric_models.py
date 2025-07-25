# /var/www/megahub/backend/crm_analytics_core/models/metric_models.py
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .base_models import AnalyticsBaseMixin

class Metric(AnalyticsBaseMixin):
    """Métrique CRM calculée"""
    
    METRIC_TYPES = [
        ('count', 'Comptage'),
        ('sum', 'Somme'),
        ('average', 'Moyenne'),
        ('percentage', 'Pourcentage'),
        ('ratio', 'Ratio'),
        ('conversion', 'Taux de Conversion'),
        ('growth', 'Croissance'),
        ('velocity', 'Vélocité'),
        ('custom', 'Personnalisé'),
    ]
    
    DATA_TYPES = [
        ('integer', 'Entier'),
        ('decimal', 'Décimal'),
        ('percentage', 'Pourcentage'),
        ('currency', 'Devise'),
        ('duration', 'Durée'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=100,
        help_text="Nom de la métrique"
    )
    display_name = models.CharField(
        max_length=150,
        help_text="Nom d'affichage"
    )
    
    # Classification
    metric_type = models.CharField(
        max_length=15,
        choices=METRIC_TYPES,
        help_text="Type de métrique"
    )
    data_type = models.CharField(
        max_length=15,
        choices=DATA_TYPES,
        help_text="Type de données"
    )
    category = models.CharField(
        max_length=50,
        blank=True,
        help_text="Catégorie de métrique"
    )
    
    # Calcul
    source_model = models.CharField(
        max_length=100,
        help_text="Modèle source des données"
    )
    calculation_formula = models.TextField(
        help_text="Formule de calcul"
    )
    aggregation_field = models.CharField(
        max_length=100,
        blank=True,
        help_text="Champ d'agrégation"
    )
    
    # Filtres par défaut
    default_filters = models.JSONField(
        default=dict,
        blank=True,
        help_text="Filtres par défaut"
    )
    
    # Valeur actuelle
    current_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Valeur actuelle"
    )
    previous_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Valeur précédente"
    )
    
    # Variation
    change_absolute = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Variation absolue"
    )
    change_percentage = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Variation en pourcentage"
    )
    
    # Seuils et alertes
    target_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Valeur cible"
    )
    warning_threshold = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Seuil d'alerte"
    )
    critical_threshold = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Seuil critique"
    )
    
    # Configuration d'affichage
    unit = models.CharField(
        max_length=20,
        blank=True,
        help_text="Unité d'affichage"
    )
    decimal_places = models.IntegerField(
        default=2,
        validators=[MinValueValidator(0), MaxValueValidator(6)],
        help_text="Nombre de décimales"
    )
    format_template = models.CharField(
        max_length=50,
        blank=True,
        help_text="Template de formatage"
    )
    
    # État
    is_active = models.BooleanField(
        default=True,
        help_text="Métrique active"
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Métrique mise en avant"
    )
    
    class Meta:
        db_table = 'crm_analytics_metric'
        ordering = ['-is_featured', 'name']
        verbose_name = 'Métrique Analytics'
        verbose_name_plural = 'Métriques Analytics'
        indexes = [
            models.Index(fields=['metric_type', 'category']),
            models.Index(fields=['source_model']),
            models.Index(fields=['is_active', 'is_featured']),
        ]
    
    def __str__(self):
        return self.display_name
    
    @property
    def status(self):
        """Statut basé sur les seuils"""
        if not self.current_value:
            return 'unknown'
        
        if self.critical_threshold:
            if self.current_value <= self.critical_threshold:
                return 'critical'
        
        if self.warning_threshold:
            if self.current_value <= self.warning_threshold:
                return 'warning'
        
        return 'good'
    
    def calculate_change(self):
        """Calcule la variation"""
        if self.current_value and self.previous_value:
            self.change_absolute = self.current_value - self.previous_value
            if self.previous_value != 0:
                self.change_percentage = (self.change_absolute / self.previous_value) * 100
            else:
                self.change_percentage = 100 if self.current_value > 0 else 0
        
        self.save(update_fields=['change_absolute', 'change_percentage'])

class MetricHistory(AnalyticsBaseMixin):
    """Historique des valeurs de métriques"""
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    metric = models.ForeignKey(
        Metric,
        on_delete=models.CASCADE,
        related_name='history',
        help_text="Métrique parent"
    )
    
    # Valeur historique
    value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Valeur de la métrique"
    )
    recorded_at = models.DateTimeField(
        help_text="Date d'enregistrement"
    )
    
    # Context
    context = models.JSONField(
        default=dict,
        blank=True,
        help_text="Contexte de la mesure"
    )
    
    class Meta:
        db_table = 'crm_metric_history'
        unique_together = ['metric', 'recorded_at']
        ordering = ['-recorded_at']
        verbose_name = 'Historique Métrique'
        verbose_name_plural = 'Historiques Métriques'
        indexes = [
            models.Index(fields=['metric', 'recorded_at']),
            models.Index(fields=['recorded_at']),
        ]
    
    def __str__(self):
        return f"{self.metric.name} - {self.value} ({self.recorded_at})"

class Chart(AnalyticsBaseMixin):
    """Graphique CRM personnalisable"""
    
    CHART_TYPES = [
        ('line', 'Courbe'),
        ('area', 'Aires'),
        ('bar', 'Barres'),
        ('column', 'Colonnes'),
        ('pie', 'Camembert'),
        ('donut', 'Donut'),
        ('scatter', 'Nuage de Points'),
        ('bubble', 'Bulles'),
        ('gauge', 'Jauge'),
        ('funnel', 'Entonnoir'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=100,
        help_text="Nom du graphique"
    )
    
    # Configuration
    chart_type = models.CharField(
        max_length=15,
        choices=CHART_TYPES,
        help_text="Type de graphique"
    )
    title = models.CharField(
        max_length=150,
        help_text="Titre du graphique"
    )
    subtitle = models.CharField(
        max_length=200,
        blank=True,
        help_text="Sous-titre"
    )
    
    # Données
    metrics = models.ManyToManyField(
        Metric,
        through='ChartMetric',
        related_name='charts',
        help_text="Métriques affichées"
    )
    
    # Configuration visuelle
    chart_config = models.JSONField(
        default=dict,
        help_text="Configuration du graphique"
    )
    color_scheme = models.CharField(
        max_length=50,
        default='default',
        help_text="Schéma de couleurs"
    )
    
    # Axes
    x_axis_label = models.CharField(
        max_length=100,
        blank=True,
        help_text="Label axe X"
    )
    y_axis_label = models.CharField(
        max_length=100,
        blank=True,
        help_text="Label axe Y"
    )
    
    # État
    is_public = models.BooleanField(
        default=False,
        help_text="Graphique public"
    )
    is_template = models.BooleanField(
        default=False,
        help_text="Template réutilisable"
    )
    
    class Meta:
        db_table = 'crm_analytics_chart'
        ordering = ['name']
        verbose_name = 'Graphique Analytics'
        verbose_name_plural = 'Graphiques Analytics'
        indexes = [
            models.Index(fields=['chart_type']),
            models.Index(fields=['is_public', 'is_template']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_chart_type_display()})"

class ChartMetric(models.Model):
    """Association Chart-Metric avec configuration"""
    
    # Relations
    chart = models.ForeignKey(
        Chart,
        on_delete=models.CASCADE,
        help_text="Graphique"
    )
    metric = models.ForeignKey(
        Metric,
        on_delete=models.CASCADE,
        help_text="Métrique"
    )
    
    # Configuration d'affichage
    display_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Nom d'affichage personnalisé"
    )
    color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Couleur hex"
    )
    line_type = models.CharField(
        max_length=20,
        blank=True,
        help_text="Type de ligne"
    )
    y_axis = models.CharField(
        max_length=10,
        choices=[('left', 'Gauche'), ('right', 'Droite')],
        default='left',
        help_text="Axe Y"
    )
    
    # Ordre
    display_order = models.IntegerField(
        default=0,
        help_text="Ordre d'affichage"
    )
    
    class Meta:
        db_table = 'crm_chart_metric'
        unique_together = ['chart', 'metric']
        ordering = ['display_order']
        verbose_name = 'Métrique Graphique'
        verbose_name_plural = 'Métriques Graphiques'
    
    def __str__(self):
        return f"{self.chart.name} - {self.metric.name}"
