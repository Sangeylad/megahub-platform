# /var/www/megahub/backend/crm_pipeline_core/models/base_models.py
from django.db import models
from crm_entities_core.models import CRMBaseMixin

class PipelineBaseMixin(CRMBaseMixin):
    """Mixin de base pour tous les éléments de pipeline"""
    
    # Métadonnées secteur
    company_category = models.ForeignKey(
        'company_categorization_core.IndustryCategory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Secteur d'application du pipeline"
    )
    
    # Configuration
    is_default = models.BooleanField(
        default=False,
        help_text="Pipeline/Stage par défaut"
    )
    sort_order = models.IntegerField(
        default=0,
        help_text="Ordre d'affichage"
    )
    
    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['company_category']),
            models.Index(fields=['is_default', 'sort_order']),
        ]
