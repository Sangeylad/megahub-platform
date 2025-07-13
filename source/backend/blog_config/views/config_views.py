# backend/blog_config/views/config_views.py

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from common.views.mixins import BrandScopedViewSetMixin
from rest_framework.permissions import IsAuthenticated
from common.permissions.business_permissions import IsBrandMember
from ..models import BlogConfig
from ..serializers import BlogConfigSerializer


class BlogConfigViewSet(BrandScopedViewSetMixin, viewsets.ModelViewSet):
    """Config blog par website"""
    queryset = BlogConfig.objects.select_related('website', 'website__brand')
    serializer_class = BlogConfigSerializer
    permission_classes = [IsAuthenticated, IsBrandMember]
    
    def get_queryset(self):
        """Filtrage par website si spécifié"""
        queryset = super().get_queryset()
        website_id = self.request.query_params.get('website_id')
        if website_id:
            queryset = queryset.filter(website_id=website_id)
        return queryset
    
    @action(detail=False, methods=['get'])
    def templates(self, request):
        """Pages templates disponibles"""
        from seo_pages_content.models import Page
        
        website_id = request.query_params.get('website_id')
        if not website_id:
            return Response({'error': 'website_id required'}, status=400)
        
        templates = Page.objects.filter(
            website_id=website_id,
            page_type__in=['blog', 'blog_category']
        ).values('id', 'title', 'page_type', 'url_path')
        
        return Response({
            'available_templates': list(templates)
        })