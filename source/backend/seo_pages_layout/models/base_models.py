# backend/seo_pages_layout/models/base_models.py

from django.db import models
from common.models.mixins import TimestampedMixin

class PageLayoutBaseModel(TimestampedMixin):
    """Classe abstraite de base pour tous les modèles seo_pages_layout"""
    
    # 🆕 AJOUTER le champ manquant pour corriger l'erreur
    created_by = models.ForeignKey(
        'users_core.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(app_label)s_%(class)s_created',
        verbose_name="Créé par"
    )
    
    class Meta:
        abstract = True