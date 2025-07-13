# backend/seo_websites_categorization/views/base_views.py

from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend

from common.views.mixins import BrandScopedViewSetMixin, BulkActionViewSetMixin

class SeoWebsitesCategorizationBaseViewSet(BrandScopedViewSetMixin, viewsets.ModelViewSet):
    """Classe abstraite de base pour tous les ViewSets seo_websites_categorization"""
    
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    ordering = ['-created_at']
    
    class Meta:
        abstract = True

class WebsiteCategorizationBulkViewSet(SeoWebsitesCategorizationBaseViewSet, BulkActionViewSetMixin):
    """Base ViewSet avec actions en masse pour categorizations"""
    
    class Meta:
        abstract = True