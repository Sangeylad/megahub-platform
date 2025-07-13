# backend/seo_websites_categorization/models/base_models.py

from django.db import models
from common.models.mixins import TimestampedMixin

class SeoWebsitesCategorizationBaseModel(TimestampedMixin):
    """Classe abstraite de base pour tous les modèles seo_websites_categorization"""
    
    class Meta:
        abstract = True