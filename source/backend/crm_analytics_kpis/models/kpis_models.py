# /var/www/megahub/backend/crm_analytics_kpis/models/kpis_models.py
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from crm_analytics_core.models import AnalyticsBaseMixin

class KPI(AnalyticsBaseMixin):
    """Key Performance Indicator CRM"""
    
    KPI_CATEGORIES = [
        ('sales', 'Ventes'),
        ('marketing', 'Marketing'),
        ('customer_service', 'Service Client'),
        ('team_performance', 'Performance Équipe'),
        ('pipeline', 'Pipeline'),
        ('retention', 'Fidélisation'),
        ('acquisition', 'Acquisition'),
        ('profitability', 'Rentabilité'),
    ]
    
    KPI_TYPES = [
        ('count', 'Compteur'),
        ('rate', 'Taux'),
        ('average', 'Moyenne'),
        ('ratio', 'Ratio'),
        ('score', 'Score'),
        ('index', 'Indice'),
        ('percentage', 'Pourcentage'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=100,
        help_text="Nom du KPI"
    )
    display_name = models.CharField(
        max_length=150,
        help_text="Nom d'affichage"
    )
    
    # Classification
    category = models.CharField(
        max_length=20,
        choices=KPI_CATEGORIES,
        help_text="Catégorie du KPI"
    )
    kpi_type = models.CharField(
        max_length=15,
        choices=KPI_TYPES,
        help_text="Type de KPI"
    )
    
    # Configuration
    description = models.TextField(
        help_text="Description du KPI"
    )
    calculation_method = models.TextField(
        help_text="Méthode de calcul"
    )
    data_sources = models.JSONField(
        default=list,
        help_text="Sources de données"
    )
    
    # Valeur actuelle
    current_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Valeur actuelle"
    )
    target_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Valeur cible"
    )
    
    # Seuils de performance
    excellent_threshold = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Seuil excellent"
    )
    good_threshold = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Seuil bon"
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
        help_text="Unité"
    )
    format_string = models.CharField(
        max_length=50,
        blank=True,
        help_text="Format d'affichage"
    )
    color_scheme = models.CharField(
        max_length=50,
        default='default',
        help_text="Schéma de couleurs"
    )
    
    # Propriétaire et responsable
    responsible_user = models.ForeignKey(
        'users_core.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='responsible_kpis',
        help_text="Responsable du KPI"
    )
    
    # État
    is_active = models.BooleanField(
        default=True,
        help_text="KPI actif"
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="KPI mis en avant"
    )
    
    # Métadonnées
    business_impact = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Faible'),
            ('medium', 'Moyen'),
            ('high', 'Élevé'),
            ('critical', 'Critique'),
        ],
        default='medium',
        help_text="Impact business"
    )
    update_frequency = models.CharField(
        max_length=20,
        choices=[
            ('real_time', 'Temps Réel'),
            ('hourly', 'Horaire'),
            ('daily', 'Quotidien'),
            ('weekly', 'Hebdomadaire'),
            ('monthly', 'Mensuel'),
        ],
        default='daily',
        help_text="Fréquence de mise à jour"
    )
    
    class Meta:
        db_table = 'crm_analytics_kpi'
        ordering = ['-is_featured', 'category', 'name']
        verbose_name = 'KPI Analytics'
        verbose_name_plural = 'KPIs Analytics'
        indexes = [
            models.Index(fields=['category', 'kpi_type']),
            models.Index(fields=['is_active', 'is_featured']),
            models.Index(fields=['business_impact']),
        ]
    
    def __str__(self):
        return self.display_name
    
    @property
    def performance_status(self):
        """Statut de performance basé sur les seuils"""
        if not self.current_value:
            return 'unknown'
        
        value = float(self.current_value)
        
        if self.excellent_threshold and value >= float(self.excellent_threshold):
            return 'excellent'
        elif self.good_threshold and value >= float(self.good_threshold):
            return 'good'
        elif self.warning_threshold and value >= float(self.warning_threshold):
            return 'warning'
        else:
            return 'critical'
    
    @property
    def target_achievement_percentage(self):
        """Pourcentage de réalisation de l'objectif"""
        if not self.current_value or not self.target_value:
            return None
        return (float(self.current_value) / float(self.target_value)) * 100

class Performance(AnalyticsBaseMixin):
    """Performance mesurée pour une entité"""
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kpi = models.ForeignKey(
        KPI,
        on_delete=models.CASCADE,
        related_name='performances',
        help_text="KPI mesuré"
    )
    
    # Entité mesurée (utilisateur, équipe, etc.)
    entity_type = models.CharField(
        max_length=50,
        help_text="Type d'entité (User, Team, Brand)"
    )
    entity_id = models.UUIDField(
        help_text="ID de l'entité"
    )
    entity_name = models.CharField(
        max_length=100,
        help_text="Nom de l'entité"
    )
    
    # Valeur de performance
    value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Valeur de la performance"
    )
    previous_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Valeur précédente"
    )
    
    # Changement
    change_absolute = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Changement absolu"
    )
    change_percentage = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Changement en pourcentage"
    )
    
    # Contexte
    context_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Données contextuelles"
    )
    notes = models.TextField(
        blank=True,
        help_text="Notes sur la performance"
    )
    
    # Dates
    measured_at = models.DateTimeField(
        help_text="Date de mesure"
    )
    
    class Meta:
        db_table = 'crm_performance'
        unique_together = ['kpi', 'entity_type', 'entity_id', 'measured_at']
        ordering = ['-measured_at']
        verbose_name = 'Performance'
        verbose_name_plural = 'Performances'
        indexes = [
            models.Index(fields=['kpi', 'entity_type', 'entity_id']),
            models.Index(fields=['measured_at']),
            models.Index(fields=['value']),
        ]
    
    def __str__(self):
        return f"{self.kpi.name} - {self.entity_name}: {self.value}"

class Benchmark(AnalyticsBaseMixin):
    """Benchmark sectoriel pour un KPI"""
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kpi = models.ForeignKey(
        KPI,
        on_delete=models.CASCADE,
        related_name='benchmarks',
        help_text="KPI benchmarké"
    )
    
    # Secteur
    industry_category = models.ForeignKey(
        'company_categorization_core.IndustryCategory',
        on_delete=models.CASCADE,
        help_text="Catégorie industrie"
    )
    
    # Statistiques benchmark
    sample_size = models.IntegerField(
        help_text="Taille de l'échantillon"
    )
    median_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Valeur médiane"
    )
    mean_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Valeur moyenne"
    )
    
    # Percentiles
    percentile_25 = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="25e percentile"
    )
    percentile_75 = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="75e percentile"
    )
    percentile_90 = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="90e percentile"
    )
    
    # Top performers
    top_10_percent_avg = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Moyenne des 10% meilleurs"
    )
    
    # Métadonnées
    data_source = models.CharField(
        max_length=100,
        help_text="Source des données"
    )
    methodology = models.TextField(
        blank=True,
        help_text="Méthodologie de calcul"
    )
    
    # Validité
    valid_from = models.DateField(
        help_text="Valide à partir de"
    )
    valid_to = models.DateField(
        help_text="Valide jusqu'à"
    )
    
    class Meta:
        db_table = 'crm_kpi_benchmark'
        unique_together = ['kpi', 'industry_category', 'valid_from']
        ordering = ['-valid_from']
        verbose_name = 'Benchmark KPI'
        verbose_name_plural = 'Benchmarks KPI'
        indexes = [
            models.Index(fields=['kpi', 'industry_category']),
            models.Index(fields=['valid_from', 'valid_to']),
        ]
    
    def __str__(self):
        return f"{self.kpi.name} - {self.industry_category.name} Benchmark"
