# backend/seo_pages_workflow/models/base_models.py

from django.db import models
from common.models.mixins import TimestampedMixin

class PageWorkflowBaseModel(TimestampedMixin):
    """Classe abstraite de base pour tous les modèles seo_pages_workflow"""
    
    class Meta:
        abstract = True
