# /var/www/megahub/backend/crm_pipeline_core/models/pipeline_models.py
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .base_models import PipelineBaseMixin

class Pipeline(PipelineBaseMixin):
    """Pipeline commercial configuré par secteur"""
    
    PIPELINE_TYPES = [
        ('sales', 'Ventes'),
        ('marketing', 'Marketing'),
        ('support', 'Support'),
        ('custom', 'Personnalisé'),
        ('renewal', 'Renouvellement'),
        ('upsell', 'Montée en Gamme'),
    ]
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=100,
        help_text="Nom du pipeline"
    )
    
    # Classification
    pipeline_type = models.CharField(
        max_length=20,
        choices=PIPELINE_TYPES,
        default='sales',
        help_text="Type de pipeline"
    )
    
    # Description
    description = models.TextField(
        blank=True,
        help_text="Description du pipeline"
    )
    
    # Configuration
    color_code = models.CharField(
        max_length=7,
        default='#6a5acd',
        help_text="Code couleur hex"
    )
    icon_name = models.CharField(
        max_length=50,
        default='funnel',
        help_text="Nom icône (Font Awesome)"
    )
    
    # Règles business
    auto_progress = models.BooleanField(
        default=False,
        help_text="Progression automatique entre stages"
    )
    requires_approval = models.BooleanField(
        default=False,
        help_text="Nécessite approbation pour progression"
    )
    
    # Métriques
    average_cycle_days = models.IntegerField(
        null=True,
        blank=True,
        help_text="Durée moyenne du cycle (jours)"
    )
    conversion_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Taux de conversion global (%)"
    )
    
    # Statut
    is_active = models.BooleanField(
        default=True,
        help_text="Pipeline actif"
    )
    
    class Meta:
        db_table = 'crm_pipeline'
        ordering = ['sort_order', 'name']
        verbose_name = 'Pipeline CRM'
        verbose_name_plural = 'Pipelines CRM'
        indexes = [
            models.Index(fields=['brand', 'pipeline_type']),
            models.Index(fields=['is_active', 'is_default']),
            models.Index(fields=['company_category', 'pipeline_type']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_pipeline_type_display()})"
    
    def get_stages_count(self):
        """Nombre de stages dans le pipeline"""
        return self.stages.filter(is_active=True).count()
    
    def get_active_opportunities_count(self):
        """Nombre d'opportunités actives dans le pipeline"""
        return self.opportunities.filter(is_closed=False).count()
    
    def get_total_pipeline_value(self):
        """Valeur totale du pipeline"""
        from django.db.models import Sum
        result = self.opportunities.filter(is_closed=False).aggregate(
            total=Sum('amount')
        )
        return result['total'] or 0
    
    def get_weighted_pipeline_value(self):
        """Valeur pondérée du pipeline (montant × probabilité)"""
        from django.db.models import Sum, F
        result = self.opportunities.filter(is_closed=False).aggregate(
            weighted_total=Sum(F('amount') * F('probability') / 100)
        )
        return result['weighted_total'] or 0
    
    def calculate_conversion_rate(self):
        """Recalcule le taux de conversion"""
        total_opps = self.opportunities.count()
        if total_opps == 0:
            self.conversion_rate = 0
        else:
            won_opps = self.opportunities.filter(is_closed=True, is_won=True).count()
            self.conversion_rate = (won_opps / total_opps) * 100
        self.save(update_fields=['conversion_rate'])
