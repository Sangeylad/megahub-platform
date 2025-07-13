# backend/seo_websites_core/views/base_views.py

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count

from common.views.mixins import BrandScopedViewSetMixin

class WebsiteCoreBaseViewSet(BrandScopedViewSetMixin, viewsets.ModelViewSet):
    """
    Classe abstraite avec optimisations de base communes
    
    Fournit :
    - Filtrage automatique par brand (via BrandScopedViewSetMixin)
    - Optimisations queryset de base (brand + pages_count)
    - Configuration DRF standard
    """
    
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Optimisations de base communes à tous les ViewSets Website
        
        Performance Strategy:
        - select_related('brand') : Évite N+1 queries sur brand
        - annotate(pages_count) : Calcul pages en une seule query
        - Base pour optimisations conditionnelles dans enfants
        """
        queryset = super().get_queryset()
        
        # Optimisations systématiques pour tous les websites
        return queryset.select_related('brand').annotate(
            pages_count=Count('pages', distinct=True)
        )
    
    class Meta:
        abstract = True