# backend/brands_design_colors/views/color_views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
import logging

from common.views.mixins import BrandScopedViewSetMixin
from common.permissions.business_permissions import IsAuthenticated, IsBrandMember

from ..models import BrandColorPalette, WebsiteColorConfig
from ..serializers import (
    BrandColorPaletteSerializer,
    WebsiteColorConfigSerializer,
    WebsiteColorConfigDetailSerializer
)

logger = logging.getLogger(__name__)

class BrandColorPaletteViewSet(BrandScopedViewSetMixin, viewsets.ModelViewSet):
    """CRUD palettes couleurs brand"""
    
    queryset = BrandColorPalette.objects.all()
    serializer_class = BrandColorPaletteSerializer
    permission_classes = [IsAuthenticated, IsBrandMember]
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filtre par brand accessible"""
        queryset = super().get_queryset()
        return queryset.select_related('brand')
    
    @action(detail=True, methods=['get'], url_path='css-variables')  # ✅ AJOUTÉ
    def css_variables(self, request, pk=None):
        """GET /design/colors/brand-palettes/{id}/css-variables/"""
        palette = self.get_object()
        
        try:
            variables = palette.to_css_variables()
            
            return Response({
                'css_variables': variables,
                'css_content': '\n'.join([f'  {key}: {value};' for key, value in variables.items()])
            })
        except Exception as e:
            logger.error(f"Erreur génération CSS variables: {e}")
            return Response({
                'error': 'Erreur lors de la génération des variables CSS'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class WebsiteColorConfigViewSet(viewsets.ModelViewSet):
    """CRUD config couleurs websites"""
    
    queryset = WebsiteColorConfig.objects.all()
    permission_classes = [IsAuthenticated, IsBrandMember]
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filtre par websites de brands accessibles"""
        queryset = super().get_queryset()
        user_brands = self.request.user.brands.all()
        return queryset.filter(website__brand__in=user_brands).select_related(
            'website', 'website__brand'
        )
    
    def get_serializer_class(self):
        """Serializer par action"""
        if self.action == 'retrieve':
            return WebsiteColorConfigDetailSerializer
        return WebsiteColorConfigSerializer
    
    @action(detail=True, methods=['get'], url_path='css-variables')  # ✅ AJOUTÉ
    def css_variables(self, request, pk=None):
        """GET /design/colors/website-configs/{id}/css-variables/"""
        config = self.get_object()
        
        try:
            variables = config.to_css_variables()
            
            return Response({
                'css_variables': variables,
                'css_content': ':root {\n' + '\n'.join([f'  {key}: {value};' for key, value in variables.items()]) + '\n}'
            })
        except Exception as e:
            logger.error(f"Erreur génération CSS variables: {e}")
            return Response({
                'error': 'Erreur lors de la génération des variables CSS'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'], url_path='reset-overrides')  # ✅ AJOUTÉ
    def reset_overrides(self, request, pk=None):
        """POST /design/colors/website-configs/{id}/reset-overrides/"""
        config = self.get_object()
        
        try:
            config.primary_override = ''
            config.secondary_override = ''
            config.accent_override = ''
            config.save()
            
            serializer = self.get_serializer(config)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Erreur reset overrides: {e}")
            return Response({
                'error': 'Erreur lors du reset des overrides'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)