# backend/brands_design_spacing/views/spacing_views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
import logging

from common.views.mixins import BrandScopedViewSetMixin
from common.permissions.business_permissions import IsAuthenticated, IsBrandMember

from ..models import BrandSpacingSystem, WebsiteLayoutConfig
from ..serializers import (
    BrandSpacingSystemSerializer,
    WebsiteLayoutConfigSerializer,
    WebsiteLayoutConfigDetailSerializer
)

logger = logging.getLogger(__name__)

class BrandSpacingSystemViewSet(BrandScopedViewSetMixin, viewsets.ModelViewSet):
    """CRUD spacing system brand"""
    
    queryset = BrandSpacingSystem.objects.all()
    serializer_class = BrandSpacingSystemSerializer
    permission_classes = [IsAuthenticated, IsBrandMember]
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related('brand')
    
    @action(detail=True, methods=['get'], url_path='tailwind-spacing')  # ✅ AJOUTÉ
    def tailwind_spacing(self, request, pk=None):
        """GET /design/spacing/brand-spacing/{id}/tailwind-spacing/"""
        spacing = self.get_object()
        
        try:
            scale = spacing.generate_spacing_scale()
            
            return Response({
                'spacing_scale': scale,
                'tailwind_config': {
                    'spacing': scale,
                    'maxWidth': {
                        'container': spacing.max_width
                    }
                }
            })
        except Exception as e:
            logger.error(f"Erreur génération spacing: {e}")
            return Response({
                'error': 'Erreur lors de la génération du spacing'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class WebsiteLayoutConfigViewSet(viewsets.ModelViewSet):
    """CRUD layout config websites"""
    
    queryset = WebsiteLayoutConfig.objects.all()
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
            return WebsiteLayoutConfigDetailSerializer
        return WebsiteLayoutConfigSerializer