# backend/brands_design_typography/views/typography_views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
import logging

from common.views.mixins import BrandScopedViewSetMixin
from common.permissions.business_permissions import IsAuthenticated, IsBrandMember

from ..models import BrandTypography, WebsiteTypographyConfig
from ..serializers import (
    BrandTypographySerializer,
    WebsiteTypographyConfigSerializer,
    WebsiteTypographyConfigDetailSerializer
)

logger = logging.getLogger(__name__)

class BrandTypographyViewSet(BrandScopedViewSetMixin, viewsets.ModelViewSet):
    """CRUD typography brand"""
    
    queryset = BrandTypography.objects.all()
    serializer_class = BrandTypographySerializer
    permission_classes = [IsAuthenticated, IsBrandMember]
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related('brand')
    
    @action(detail=True, methods=['get'], url_path='font-sizes')  # ✅ AJOUTÉ
    def font_sizes(self, request, pk=None):
        """GET /design/typography/brand-typography/{id}/font-sizes/"""
        typography = self.get_object()
        
        try:
            sizes = typography.generate_font_sizes()
            
            return Response({
                'font_sizes': sizes,
                'tailwind_config': {
                    'fontSize': sizes
                }
            })
        except Exception as e:
            logger.error(f"Erreur génération font sizes: {e}")
            return Response({
                'error': 'Erreur lors de la génération des tailles de police'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class WebsiteTypographyConfigViewSet(viewsets.ModelViewSet):
    """CRUD config typography websites"""
    
    queryset = WebsiteTypographyConfig.objects.all()
    permission_classes = [IsAuthenticated, IsBrandMember]
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user_brands = self.request.user.brands.all()
        return queryset.filter(website__brand__in=user_brands).select_related(
            'website', 'website__brand'
        )
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return WebsiteTypographyConfigDetailSerializer
        return WebsiteTypographyConfigSerializer
    
    @action(detail=True, methods=['get'], url_path='font-sizes')  # ✅ AJOUTÉ
    def font_sizes(self, request, pk=None):
        """GET /design/typography/website-configs/{id}/font-sizes/"""
        config = self.get_object()
        
        try:
            sizes = config.generate_effective_font_sizes()
            
            return Response({
                'font_sizes': sizes,
                'tailwind_config': {
                    'fontSize': sizes,
                    'fontFamily': {
                        'sans': [config.get_effective_font_primary(), 'sans-serif']
                    }
                }
            })
        except Exception as e:
            logger.error(f"Erreur génération font sizes: {e}")
            return Response({
                'error': 'Erreur lors de la génération des tailles de police'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)