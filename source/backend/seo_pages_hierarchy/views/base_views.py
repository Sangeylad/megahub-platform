# backend/seo_pages_hierarchy/views/base_views.py

from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend

from common.views.mixins import BrandScopedViewSetMixin
from common.permissions.business_permissions import IsAuthenticated, IsBrandMember

class PageHierarchyBaseViewSet(BrandScopedViewSetMixin, viewsets.ModelViewSet):
    """Classe abstraite de base pour tous les ViewSets seo_pages_hierarchy"""
    
    permission_classes = [IsAuthenticated, IsBrandMember]
    filter_backends = [DjangoFilterBackend]
    ordering = ['-created_at']
    
    class Meta:
        abstract = True