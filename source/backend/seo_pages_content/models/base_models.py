# backend/seo_pages_content/models/base_models.py

from django.db import models
from common.models.mixins import TimestampedMixin

class PageContentBaseModel(TimestampedMixin):
    """Classe abstraite de base pour tous les modèles seo_pages_content"""
    
    class Meta:
        abstract = True
