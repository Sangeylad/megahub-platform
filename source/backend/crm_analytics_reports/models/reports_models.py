# /var/www/megahub/backend/crm_analytics_reports/models/reports_models.py
import uuid
from django.db import models
from crm_analytics_core.models import AnalyticsBaseMixin

class Report(AnalyticsBaseMixin):
    """Rapport CRM personnalisable"""
    
    REPORT_TYPES = [
        ('summary', 'Résumé'),
        ('detailed', 'Détaillé'),
        ('comparative', 'Comparatif'),
        ('trend', 'Tendance'),
        ('performance', 'Performance'),
        ('forecast', 'Prévisionnel'),
        ('custom', 'Personnalisé'),
    ]
    
    OUTPUT_FORMATS = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('json', 'JSON'),
        ('html', 'HTML'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=100,
        help_text="Nom du rapport"
    )
    
    # Classification
    report_type = models.CharField(
        max_length=15,
        choices=REPORT_TYPES,
        help_text="Type de rapport"
    )
    category = models.CharField(
        max_length=50,
        blank=True,
        help_text="Catégorie"
    )
    description = models.TextField(
        blank=True,
        help_text="Description du rapport"
    )
    
    # Configuration
    data_sources = models.JSONField(
        default=list,
        help_text="Sources de données"
    )
    filters = models.JSONField(
        default=dict,
        blank=True,
        help_text="Filtres par défaut"
    )
    sections = models.JSONField(
        default=list,
        help_text="Sections du rapport"
    )
    
    # Formatage
    template = models.TextField(
        blank=True,
        help_text="Template du rapport"
    )
    output_format = models.CharField(
        max_length=10,
        choices=OUTPUT_FORMATS,
        default='pdf',
        help_text="Format de sortie"
    )
    
    # Planification
    is_scheduled = models.BooleanField(
        default=False,
        help_text="Rapport programmé"
    )
    schedule_config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Configuration programmation"
    )
    
    # Distribution
    recipients = models.ManyToManyField(
        'users_core.CustomUser',
        through='ReportRecipient',
        related_name='subscribed_reports',
        blank=True,
        help_text="Destinataires"
    )
    
    # État
    is_active = models.BooleanField(
        default=True,
        help_text="Rapport actif"
    )
    is_template = models.BooleanField(
        default=False,
        help_text="Template réutilisable"
    )
    
    # Statistiques
    generation_count = models.IntegerField(
        default=0,
        help_text="Nombre de générations"
    )
    last_generated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Dernière génération"
    )
    
    class Meta:
        db_table = 'crm_analytics_report'
        ordering = ['name']
        verbose_name = 'Rapport Analytics'
        verbose_name_plural = 'Rapports Analytics'
        indexes = [
            models.Index(fields=['report_type', 'category']),
            models.Index(fields=['is_scheduled', 'is_active']),
            models.Index(fields=['last_generated_at']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_report_type_display()})"

class ReportGeneration(AnalyticsBaseMixin):
    """Génération d'un rapport"""
    
    GENERATION_STATUS = [
        ('pending', 'En attente'),
        ('generating', 'En cours'),
        ('completed', 'Terminé'),
        ('failed', 'Échoué'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name='generations',
        help_text="Rapport généré"
    )
    
    # État
    status = models.CharField(
        max_length=15,
        choices=GENERATION_STATUS,
        default='pending',
        help_text="Statut de génération"
    )
    
    # Dates
    requested_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Demandé à"
    )
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Démarré à"
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Terminé à"
    )
    
    # Paramètres de génération
    generation_params = models.JSONField(
        default=dict,
        help_text="Paramètres de génération"
    )
    filters_applied = models.JSONField(
        default=dict,
        help_text="Filtres appliqués"
    )
    
    # Résultat
    file_path = models.CharField(
        max_length=500,
        blank=True,
        help_text="Chemin du fichier généré"
    )
    file_size = models.IntegerField(
        null=True,
        blank=True,
        help_text="Taille du fichier (bytes)"
    )
    error_message = models.TextField(
        blank=True,
        help_text="Message d'erreur"
    )
    
    # Métadonnées
    generated_by = models.ForeignKey(
        'users_core.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='generated_reports',
        help_text="Généré par"
    )
    
    class Meta:
        db_table = 'crm_report_generation'
        ordering = ['-requested_at']
        verbose_name = 'Génération Rapport'
        verbose_name_plural = 'Générations Rapports'
        indexes = [
            models.Index(fields=['report', 'status']),
            models.Index(fields=['requested_at']),
        ]
    
    def __str__(self):
        return f"{self.report.name} - {self.status} ({self.requested_at})"

class ReportRecipient(models.Model):
    """Destinataire de rapport"""
    
    DELIVERY_METHODS = [
        ('email', 'Email'),
        ('download', 'Téléchargement'),
        ('webhook', 'Webhook'),
    ]
    
    # Relations
    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        help_text="Rapport"
    )
    user = models.ForeignKey(
        'users_core.CustomUser',
        on_delete=models.CASCADE,
        help_text="Destinataire"
    )
    
    # Configuration
    delivery_method = models.CharField(
        max_length=15,
        choices=DELIVERY_METHODS,
        default='email',
        help_text="Méthode de livraison"
    )
    custom_filters = models.JSONField(
        default=dict,
        blank=True,
        help_text="Filtres personnalisés"
    )
    
    # État
    is_active = models.BooleanField(
        default=True,
        help_text="Abonnement actif"
    )
    subscribed_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Abonné le"
    )
    
    class Meta:
        db_table = 'crm_report_recipient'
        unique_together = ['report', 'user']
        verbose_name = 'Destinataire Rapport'
        verbose_name_plural = 'Destinataires Rapports'
    
    def __str__(self):
        return f"{self.report.name} → {self.user.get_full_name()}"

class ReportFilter(AnalyticsBaseMixin):
    """Filtre de rapport réutilisable"""
    
    FILTER_TYPES = [
        ('date_range', 'Plage de Dates'),
        ('single_value', 'Valeur Unique'),
        ('multiple_values', 'Valeurs Multiples'),
        ('range', 'Plage'),
        ('boolean', 'Booléen'),
        ('text_search', 'Recherche Texte'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=100,
        help_text="Nom du filtre"
    )
    
    # Configuration
    filter_type = models.CharField(
        max_length=20,
        choices=FILTER_TYPES,
        help_text="Type de filtre"
    )
    field_name = models.CharField(
        max_length=100,
        help_text="Nom du champ"
    )
    operator = models.CharField(
        max_length=20,
        help_text="Opérateur"
    )
    
    # Options
    options = models.JSONField(
        default=list,
        blank=True,
        help_text="Options disponibles"
    )
    default_value = models.JSONField(
        null=True,
        blank=True,
        help_text="Valeur par défaut"
    )
    
    # Configuration d'affichage
    label = models.CharField(
        max_length=100,
        help_text="Label d'affichage"
    )
    placeholder = models.CharField(
        max_length=100,
        blank=True,
        help_text="Placeholder"
    )
    help_text = models.CharField(
        max_length=200,
        blank=True,
        help_text="Texte d'aide"
    )
    
    # État
    is_required = models.BooleanField(
        default=False,
        help_text="Filtre obligatoire"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Filtre actif"
    )
    
    class Meta:
        db_table = 'crm_report_filter'
        ordering = ['name']
        verbose_name = 'Filtre Rapport'
        verbose_name_plural = 'Filtres Rapports'
        indexes = [
            models.Index(fields=['filter_type']),
            models.Index(fields=['field_name']),
        ]
    
    def __str__(self):
        return self.label or self.name
