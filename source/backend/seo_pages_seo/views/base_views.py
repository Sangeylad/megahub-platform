# backend/seo_pages_seo/views/base_views.py

from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend

from common.views.mixins import BrandScopedViewSetMixin
from common.permissions.business_permissions import IsAuthenticated, IsBrandMember

class PageSeoBaseViewSet(BrandScopedViewSetMixin, viewsets.ModelViewSet):
    """Classe abstraite de base pour tous les ViewSets seo_pages_seo"""
    
    # 🎯 AJOUTER IsBrandMember
    permission_classes = [IsAuthenticated, IsBrandMember]
    filter_backends = [DjangoFilterBackend]
    ordering = ['-created_at']
    
    class Meta:
        abstract = True