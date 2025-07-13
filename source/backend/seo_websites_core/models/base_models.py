# backend/seo_websites_core/models/base_models.py

from django.db import models
from common.models.mixins import TimestampedMixin

class WebsiteCoreBaseModel(TimestampedMixin):
    """Classe abstraite de base pour tous les modèles seo_websites_core"""
    
    class Meta:
        abstract = True
