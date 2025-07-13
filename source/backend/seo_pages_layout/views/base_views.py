# backend/seo_pages_layout/views/base_views.py

from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend

from common.views.mixins import BrandScopedViewSetMixin
from common.permissions.business_permissions import IsBrandMember

class PageLayoutBaseViewSet(BrandScopedViewSetMixin, viewsets.ModelViewSet):
    """
    Classe abstraite de base pour tous les ViewSets seo_pages_layout
    
    Hérite de BrandScopedViewSetMixin pour filtrage automatique par brand
    """
    
    permission_classes = [permissions.IsAuthenticated, IsBrandMember]
    filter_backends = [DjangoFilterBackend]
    ordering = ['-created_at']
    
    class Meta:
        abstract = True