# /var/www/megahub/backend/crm_workflow_core/models/base_models.py
from django.db import models
from crm_entities_core.models import CRMBaseMixin

class WorkflowBaseMixin(CRMBaseMixin):
    """Mixin de base pour tous les éléments de workflow"""
    
    # Métadonnées secteur
    company_category = models.ForeignKey(
        'company_categorization_core.IndustryCategory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Secteur d'application du workflow"
    )
    
    # Configuration
    is_template = models.BooleanField(
        default=False,
        help_text="Élément template (réutilisable)"
    )
    version = models.CharField(
        max_length=20,
        default='1.0',
        help_text="Version"
    )
    
    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['company_category']),
            models.Index(fields=['is_template', 'version']),
        ]
