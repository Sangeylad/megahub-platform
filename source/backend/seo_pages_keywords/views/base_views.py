# backend/seo_pages_keywords/views/base_views.py

from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend

from common.views.mixins import BrandScopedViewSetMixin

class PageKeywordsBaseViewSet(BrandScopedViewSetMixin, viewsets.ModelViewSet):
    """Classe abstraite de base pour tous les ViewSets seo_pages_keywords"""
    
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    ordering = ['-created_at']
    
    class Meta:
        abstract = True
