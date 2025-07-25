# /var/www/megahub/backend/crm_analytics_core/models/dashboard_models.py
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .base_models import AnalyticsBaseMixin

class Dashboard(AnalyticsBaseMixin):
    """Tableau de bord CRM personnalisable"""
    
    DASHBOARD_TYPES = [
        ('overview', 'Vue d\'ensemble'),
        ('sales', 'Ventes'),
        ('marketing', 'Marketing'),
        ('support', 'Support'),
        ('team_performance', 'Performance Équipe'),
        ('pipeline', 'Pipeline'),
        ('forecasting', 'Prévisions'),
        ('custom', 'Personnalisé'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=100,
        help_text="Nom du tableau de bord"
    )
    
    # Classification
    dashboard_type = models.CharField(
        max_length=20,
        choices=DASHBOARD_TYPES,
        help_text="Type de tableau de bord"
    )
    description = models.TextField(
        blank=True,
        help_text="Description du tableau de bord"
    )
    
    # Configuration
    layout_config = models.JSONField(
        default=dict,
        help_text="Configuration de la mise en page"
    )
    refresh_interval_minutes = models.IntegerField(
        default=60,
        help_text="Intervalle de rafraîchissement (minutes)"
    )
    
    # Partage
    is_public = models.BooleanField(
        default=False,
        help_text="Dashboard public"
    )
    shared_with = models.ManyToManyField(
        'users_core.CustomUser',
        through='DashboardShare',
        through_fields=('dashboard', 'user'),
        related_name='shared_dashboards',
        blank=True,
        help_text="Partagé avec"
    )
    
    # Métadonnées
    is_default = models.BooleanField(
        default=False,
        help_text="Dashboard par défaut"
    )
    is_template = models.BooleanField(
        default=False,
        help_text="Template réutilisable"
    )
    
    # Statistiques
    view_count = models.IntegerField(
        default=0,
        help_text="Nombre de vues"
    )
    last_viewed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Dernière consultation"
    )
    
    class Meta:
        db_table = 'crm_analytics_dashboard'
        ordering = ['-is_default', 'name']
        verbose_name = 'Dashboard Analytics'
        verbose_name_plural = 'Dashboards Analytics'
        indexes = [
            models.Index(fields=['dashboard_type', 'is_public']),
            models.Index(fields=['is_default', 'is_template']),
            models.Index(fields=['last_viewed_at']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_dashboard_type_display()})"
    
    def increment_view_count(self):
        """Incrémente le compteur de vues"""
        from django.utils import timezone
        self.view_count += 1
        self.last_viewed_at = timezone.now()
        self.save(update_fields=['view_count', 'last_viewed_at'])

class DashboardShare(models.Model):
    """Partage de dashboards"""
    
    PERMISSION_LEVELS = [
        ('view', 'Visualisation'),
        ('interact', 'Interaction'),
        ('edit', 'Modification'),
    ]
    
    # Relations
    dashboard = models.ForeignKey(
        Dashboard,
        on_delete=models.CASCADE,
        help_text="Dashboard partagé"
    )
    user = models.ForeignKey(
        'users_core.CustomUser',
        on_delete=models.CASCADE,
        help_text="Utilisateur"
    )
    
    # Permission
    permission = models.CharField(
        max_length=10,
        choices=PERMISSION_LEVELS,
        default='view',
        help_text="Niveau de permission"
    )
    
    # Dates
    shared_date = models.DateTimeField(
        auto_now_add=True,
        help_text="Date de partage"
    )
    shared_by = models.ForeignKey(
        'users_core.CustomUser',
        on_delete=models.CASCADE,
        related_name='dashboard_shares_granted',
        help_text="Partagé par"
    )
    
    class Meta:
        db_table = 'crm_dashboard_share'
        unique_together = ['dashboard', 'user']
        verbose_name = 'Partage Dashboard'
        verbose_name_plural = 'Partages Dashboard'
    
    def __str__(self):
        return f"{self.dashboard.name} → {self.user.get_full_name()}"

class DashboardWidget(AnalyticsBaseMixin):
    """Widget dans un tableau de bord"""
    
    WIDGET_TYPES = [
        ('metric', 'Métrique Simple'),
        ('chart_line', 'Graphique Linéaire'),
        ('chart_bar', 'Graphique Barres'),
        ('chart_pie', 'Graphique Camembert'),
        ('chart_donut', 'Graphique Donut'),
        ('table', 'Tableau'),
        ('gauge', 'Jauge'),
        ('kpi_card', 'Carte KPI'),
        ('leaderboard', 'Classement'),
        ('timeline', 'Timeline'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dashboard = models.ForeignKey(
        Dashboard,
        on_delete=models.CASCADE,
        related_name='widgets',
        help_text="Dashboard parent"
    )
    
    # Configuration
    title = models.CharField(
        max_length=100,
        help_text="Titre du widget"
    )
    widget_type = models.CharField(
        max_length=20,
        choices=WIDGET_TYPES,
        help_text="Type de widget"
    )
    
    # Position et taille
    position_x = models.IntegerField(
        default=0,
        help_text="Position X dans la grille"
    )
    position_y = models.IntegerField(
        default=0,
        help_text="Position Y dans la grille"
    )
    width = models.IntegerField(
        default=4,
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        help_text="Largeur (1-12)"
    )
    height = models.IntegerField(
        default=4,
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        help_text="Hauteur (1-12)"
    )
    
    # Données et configuration
    data_source = models.CharField(
        max_length=100,
        help_text="Source des données"
    )
    query_config = models.JSONField(
        default=dict,
        help_text="Configuration de la requête"
    )
    chart_config = models.JSONField(
        default=dict,
        help_text="Configuration du graphique"
    )
    
    # Filtres
    filters = models.JSONField(
        default=dict,
        blank=True,
        help_text="Filtres appliqués"
    )
    
    # Cache des données
    cached_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Données en cache"
    )
    cache_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Expiration du cache"
    )
    
    # État
    is_visible = models.BooleanField(
        default=True,
        help_text="Widget visible"
    )
    
    class Meta:
        db_table = 'crm_dashboard_widget'
        ordering = ['dashboard', 'position_y', 'position_x']
        verbose_name = 'Widget Dashboard'
        verbose_name_plural = 'Widgets Dashboard'
        indexes = [
            models.Index(fields=['dashboard', 'is_visible']),
            models.Index(fields=['widget_type']),
            models.Index(fields=['cache_expires_at']),
        ]
    
    def __str__(self):
        return f"{self.dashboard.name} - {self.title}"
    
    @property
    def is_cache_valid(self):
        """Vérifie si le cache est valide"""
        from django.utils import timezone
        return (
            self.cache_expires_at and 
            self.cache_expires_at > timezone.now()
        )
