# backend/seo_pages_keywords/models/base_models.py

from django.db import models
from common.models.mixins import TimestampedMixin

class PageKeywordsBaseModel(TimestampedMixin):
    """Classe abstraite de base pour tous les modèles seo_pages_keywords"""
    
    class Meta:
        abstract = True
