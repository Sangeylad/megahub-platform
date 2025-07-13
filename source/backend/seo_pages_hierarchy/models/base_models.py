# backend/seo_pages_hierarchy/models/base_models.py

from django.db import models
from common.models.mixins import TimestampedMixin

class PageHierarchyBaseModel(TimestampedMixin):
    """Classe abstraite de base pour tous les modèles seo_pages_hierarchy"""
    
    class Meta:
        abstract = True
