# /var/www/megahub/backend/crm_entities_enrichment/models/enrichment_models.py
import uuid
from django.db import models
from crm_entities_core.models import CRMBaseMixin

class DataEnrichment(CRMBaseMixin):
    """Enrichissement de données pour les entités CRM"""
    
    ENTITY_TYPES = [
        ('account', 'Compte'),
        ('contact', 'Contact'),
        ('opportunity', 'Opportunité'),
    ]
    
    ENRICHMENT_SOURCES = [
        ('linkedin', 'LinkedIn'),
        ('clearbit', 'Clearbit'),
        ('hunter_io', 'Hunter.io'),
        ('zoominfo', 'ZoomInfo'),
        ('apollo', 'Apollo'),
        ('lusha', 'Lusha'),
        ('societe_com', 'Société.com'),
        ('sirene', 'Base Sirene'),
        ('google_places', 'Google Places'),
        ('manual', 'Manuel'),
        ('import', 'Import'),
        ('api_custom', 'API Custom'),
    ]
    
    ENRICHMENT_TYPES = [
        ('basic_info', 'Informations de Base'),
        ('contact_info', 'Coordonnées'),
        ('social_profiles', 'Profils Sociaux'),
        ('company_data', 'Données Entreprise'),
        ('financial_data', 'Données Financières'),
        ('news_mentions', 'Mentions Presse'),
        ('technology_stack', 'Stack Technologique'),
        ('employee_data', 'Données Employés'),
        ('competitor_analysis', 'Analyse Concurrence'),
    ]
    
    QUALITY_LEVELS = [
        ('low', 'Faible'),
        ('medium', 'Moyenne'),
        ('high', 'Élevée'),
        ('verified', 'Vérifiée'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Entité enrichie
    entity_type = models.CharField(
        max_length=15,
        choices=ENTITY_TYPES,
        help_text="Type d'entité enrichie"
    )
    entity_id = models.UUIDField(
        help_text="ID de l'entité enrichie"
    )
    
    # Source et type d'enrichissement
    source = models.CharField(
        max_length=20,
        choices=ENRICHMENT_SOURCES,
        help_text="Source d'enrichissement"
    )
    enrichment_type = models.CharField(
        max_length=20,
        choices=ENRICHMENT_TYPES,
        help_text="Type d'enrichissement"
    )
    
    # Données enrichies
    enriched_data = models.JSONField(
        default=dict,
        help_text="Données enrichies en JSON"
    )
    raw_response = models.JSONField(
        default=dict,
        blank=True,
        help_text="Réponse brute de l'API"
    )
    
    # Qualité et confiance
    quality_score = models.CharField(
        max_length=10,
        choices=QUALITY_LEVELS,
        default='medium',
        help_text="Niveau de qualité"
    )
    confidence_score = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Score de confiance (0-1)"
    )
    
    # Métadonnées
    fields_enriched = models.JSONField(
        default=list,
        help_text="Liste des champs enrichis"
    )
    fields_updated = models.JSONField(
        default=list,
        help_text="Liste des champs mis à jour"
    )
    
    # Statut
    is_applied = models.BooleanField(
        default=False,
        help_text="Enrichissement appliqué à l'entité"
    )
    applied_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date d'application"
    )
    applied_by = models.ForeignKey(
        'users_core.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='applied_enrichments',
        help_text="Utilisateur qui a appliqué"
    )
    
    # Coûts et limites
    api_cost = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Coût API pour cet enrichissement"
    )
    credits_consumed = models.IntegerField(
        null=True,
        blank=True,
        help_text="Crédits consommés"
    )
    
    # Validation
    is_validated = models.BooleanField(
        default=False,
        help_text="Données validées"
    )
    validated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date de validation"
    )
    validated_by = models.ForeignKey(
        'users_core.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='validated_enrichments',
        help_text="Utilisateur qui a validé"
    )
    
    # Expiration
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date d'expiration des données"
    )
    refresh_needed = models.BooleanField(
        default=False,
        help_text="Rafraîchissement nécessaire"
    )
    
    class Meta:
        db_table = 'crm_data_enrichment'
        unique_together = ['entity_type', 'entity_id', 'source', 'enrichment_type']
        ordering = ['-created_at']
        verbose_name = 'Enrichissement Données'
        verbose_name_plural = 'Enrichissements Données'
        indexes = [
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['source', 'enrichment_type']),
            models.Index(fields=['is_applied', 'is_validated']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.get_entity_type_display()} {self.entity_id} - {self.get_enrichment_type_display()} ({self.source})"
    
    def apply_enrichment(self, user=None):
        """Applique l'enrichissement à l'entité cible"""
        if self.is_applied:
            return False
        
        # Logique d'application selon le type d'entité
        entity_model = self.get_entity_model()
        if not entity_model:
            return False
        
        try:
            entity = entity_model.objects.get(id=self.entity_id)
            
            # Appliquer les champs enrichis
            for field_name, value in self.enriched_data.items():
                if hasattr(entity, field_name) and value:
                    setattr(entity, field_name, value)
            
            entity.save()
            
            # Marquer comme appliqué
            self.is_applied = True
            self.applied_at = timezone.now()
            if user:
                self.applied_by = user
            self.save(update_fields=['is_applied', 'applied_at', 'applied_by'])
            
            return True
        except entity_model.DoesNotExist:
            return False
    
    def get_entity_model(self):
        """Retourne le modèle de l'entité selon son type"""
        from crm_entities_core.models import Account, Contact, Opportunity
        
        models_map = {
            'account': Account,
            'contact': Contact,
            'opportunity': Opportunity,
        }
        return models_map.get(self.entity_type)

class EnrichmentProvider(CRMBaseMixin):
    """Configuration des fournisseurs d'enrichissement"""
    
    PROVIDER_TYPES = [
        ('api', 'API'),
        ('file_import', 'Import Fichier'),
        ('manual', 'Manuel'),
        ('webhook', 'Webhook'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Actif'),
        ('inactive', 'Inactif'),
        ('error', 'Erreur'),
        ('rate_limited', 'Limite Dépassée'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Configuration
    name = models.CharField(
        max_length=100,
        help_text="Nom du fournisseur"
    )
    provider_key = models.CharField(
        max_length=50,
        unique=True,
        help_text="Clé unique du fournisseur"
    )
    provider_type = models.CharField(
        max_length=15,
        choices=PROVIDER_TYPES,
        help_text="Type de fournisseur"
    )
    
    # Configuration API
    api_endpoint = models.URLField(
        blank=True,
        help_text="Endpoint API"
    )
    api_key = models.CharField(
        max_length=255,
        blank=True,
        help_text="Clé API (chiffrée)"
    )
    headers = models.JSONField(
        default=dict,
        blank=True,
        help_text="Headers par défaut"
    )
    
    # Limites et coûts
    daily_limit = models.IntegerField(
        null=True,
        blank=True,
        help_text="Limite quotidienne d'appels"
    )
    monthly_limit = models.IntegerField(
        null=True,
        blank=True,
        help_text="Limite mensuelle d'appels"
    )
    cost_per_call = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        null=True,
        blank=True,
        help_text="Coût par appel"
    )
    
    # Statistiques
    total_calls = models.IntegerField(
        default=0,
        help_text="Total d'appels effectués"
    )
    successful_calls = models.IntegerField(
        default=0,
        help_text="Appels réussis"
    )
    failed_calls = models.IntegerField(
        default=0,
        help_text="Appels échoués"
    )
    
    # Statut
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='active',
        help_text="Statut du fournisseur"
    )
    last_call_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Dernier appel"
    )
    
    class Meta:
        db_table = 'crm_enrichment_provider'
        ordering = ['name']
        verbose_name = 'Fournisseur Enrichissement'
        verbose_name_plural = 'Fournisseurs Enrichissement'
        indexes = [
            models.Index(fields=['provider_key']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_provider_type_display()})"
    
    @property
    def success_rate(self):
        """Taux de succès des appels"""
        if self.total_calls == 0:
            return 0
        return (self.successful_calls / self.total_calls) * 100
    
    def increment_call_stats(self, success=True):
        """Incrémente les statistiques d'appels"""
        self.total_calls += 1
        if success:
            self.successful_calls += 1
        else:
            self.failed_calls += 1
        self.last_call_at = timezone.now()
        self.save(update_fields=[
            'total_calls', 'successful_calls', 'failed_calls', 'last_call_at'
        ])
