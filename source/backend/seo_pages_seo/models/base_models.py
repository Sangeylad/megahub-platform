# backend/seo_pages_seo/models/base_models.py

from django.db import models
from common.models.mixins import TimestampedMixin

class PageSeoBaseModel(TimestampedMixin):
    """Classe abstraite de base pour tous les modèles seo_pages_seo"""
    
    class Meta:
        abstract = True
