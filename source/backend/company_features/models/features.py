# backend/company_features/models/features.py
from django.db import models
from django.utils import timezone
from common.models.mixins import TimestampedMixin

class Feature(TimestampedMixin):
    """Features disponibles sur la plateforme"""
    
    FEATURE_TYPES = [
        ('websites', 'Sites Web'),
        ('templates', 'Templates IA'),
        ('tasks', 'Gestion de tâches'),
        ('analytics', 'Analytics'),
        ('crm', 'CRM'),
        ('integrations', 'Intégrations'),
    ]
    
    name = models.CharField(
        max_length=100, 
        unique=True,
        help_text="Nom technique de la feature"
    )
    display_name = models.CharField(
        max_length=150,
        help_text="Nom d'affichage de la feature"
    )
    description = models.TextField(
        help_text="Description détaillée de la feature"
    )
    feature_type = models.CharField(
        max_length=20,
        choices=FEATURE_TYPES,
        default='websites',
        help_text="Type de feature"
    )
    
    # Configuration
    is_active = models.BooleanField(
        default=True,
        help_text="Feature disponible sur la plateforme"
    )
    is_premium = models.BooleanField(
        default=False,
        help_text="Feature premium (payante)"
    )
    
    # Ordre d'affichage
    sort_order = models.IntegerField(
        default=0,
        help_text="Ordre d'affichage dans l'interface"
    )
    
    class Meta:
        db_table = 'feature'
        ordering = ['sort_order', 'display_name']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['is_premium']),
            models.Index(fields=['feature_type']),
        ]
    
    def __str__(self):
        return self.display_name

class CompanyFeature(TimestampedMixin):
    """Association entre Company et Features - Gestion des abonnements features"""
    
    company = models.ForeignKey(
        'company_core.Company',
        on_delete=models.CASCADE,
        related_name='company_features',
        help_text="Entreprise abonnée à la feature"
    )
    feature = models.ForeignKey(
        Feature,
        on_delete=models.CASCADE,
        related_name='subscribed_companies',
        help_text="Feature souscrite"
    )
    
    # Configuration par entreprise
    is_enabled = models.BooleanField(
        default=True,
        help_text="Feature activée pour cette entreprise"
    )
    
    # Limites par feature si applicable
    usage_limit = models.IntegerField(
        null=True,
        blank=True,
        help_text="Limite d'utilisation pour cette feature (null = illimité)"
    )
    current_usage = models.IntegerField(
        default=0,
        help_text="Utilisation actuelle"
    )
    
    # Dates d'abonnement
    subscribed_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date de souscription à la feature"
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date d'expiration (null = pas d'expiration)"
    )
    
    class Meta:
        db_table = 'company_feature'
        unique_together = ['company', 'feature']
        indexes = [
            models.Index(fields=['is_enabled']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['company', 'is_enabled']),
        ]
    
    def __str__(self):
        return f"{self.company.name} - {self.feature.display_name}"
    
    def is_active(self):
        """Vérifie si la feature est active pour cette entreprise"""
        if not self.is_enabled or not self.feature.is_active:
            return False
        
        # Vérifier l'expiration
        if self.expires_at:
            return timezone.now() <= self.expires_at
        
        return True
    
    def is_usage_limit_reached(self):
        """Vérifie si la limite d'utilisation est atteinte"""
        if self.usage_limit is None:
            return False
        return self.current_usage >= self.usage_limit
    
    def get_usage_percentage(self):
        """Pourcentage d'utilisation de la feature"""
        if self.usage_limit is None:
            return 0
        if self.usage_limit == 0:
            return 100
        return round((self.current_usage / self.usage_limit) * 100, 2)
    
    def increment_usage(self, amount=1):
        """Incrémente l'utilisation de la feature"""
        self.current_usage += amount
        self.save(update_fields=['current_usage', 'updated_at'])
    
    def reset_usage(self):
        """Remet à zéro l'utilisation (utile pour les limites mensuelles)"""
        self.current_usage = 0
        self.save(update_fields=['current_usage', 'updated_at'])

class FeatureUsageLog(TimestampedMixin):
    """Log d'utilisation des features - Pour analytics et facturation"""
    
    company_feature = models.ForeignKey(
        'company_features.CompanyFeature',  # ← FIX: Référence complète
        on_delete=models.CASCADE,
        related_name='usage_logs'
    )
    
    # Détails de l'utilisation
    action = models.CharField(
        max_length=100,
        help_text="Action effectuée (ex: 'website_created', 'ai_request')"
    )
    quantity = models.IntegerField(
        default=1,
        help_text="Quantité utilisée"
    )
    
    # Contexte
    user = models.ForeignKey(
        'users_core.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Utilisateur qui a effectué l'action"
    )
    
    brand = models.ForeignKey(
        'brands_core.Brand',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Brand concernée par l'action"
    )
    
    # Métadonnées
    metadata = models.JSONField(
        default=dict, 
        blank=True,
        help_text="Données supplémentaires en JSON"
    )
    
    class Meta:
        db_table = 'feature_usage_log'
        verbose_name = 'Feature Usage Log'
        verbose_name_plural = 'Feature Usage Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company_feature', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['action']),
        ]
    
    def __str__(self):
        return f"{self.company_feature.feature.name} - {self.action} ({self.quantity})"