# backend/seo_pages_seo/views/seo_views.py

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction

from .base_views import PageSeoBaseViewSet
from ..models import PageSEO, PagePerformance
from ..serializers import (
    PageSEOSerializer,
    PageSEOBulkUpdateSerializer,
    PagePerformanceSerializer,
    PageSitemapSerializer,
    SitemapGenerationSerializer
)

class PageSEOViewSet(PageSeoBaseViewSet):
    """
    ViewSet pour configuration SEO des pages
    """
    
    serializer_class = PageSEOSerializer
    filterset_fields = ['exclude_from_sitemap', 'sitemap_changefreq']
    
    def get_queryset(self):
        # 🎯 Le mixin gère le filtrage automatiquement
        return PageSEO.objects.select_related(
            'page',
            'page__website',
            'page__website__brand'
        )
    
    def perform_create(self, serializer):
        """Auto-assign sitemap defaults si nouvelle config"""
        page_seo = serializer.save()
        page_seo.auto_assign_sitemap_defaults()
        page_seo.save()
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Mise à jour en masse des configurations SEO"""
        serializer = PageSEOBulkUpdateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        page_ids = serializer.validated_data['page_ids']
        update_fields = {}
        
        # Construire les champs à mettre à jour
        for field in ['sitemap_priority', 'sitemap_changefreq', 'exclude_from_sitemap']:
            if field in serializer.validated_data:
                update_fields[field] = serializer.validated_data[field]
        
        if not update_fields:
            return Response(
                {'error': 'Aucun champ à mettre à jour'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mise à jour en masse
        updated_count = self.get_queryset().filter(
            page_id__in=page_ids
        ).update(**update_fields)
        
        return Response({
            'updated_count': updated_count,
            'total_requested': len(page_ids),
            'updated_fields': list(update_fields.keys())
        })
    
    @action(detail=False, methods=['get'])
    def sitemap_data(self, request):
        """Données pour génération sitemap XML"""
        website_id = request.query_params.get('website_id')
        include_drafts = request.query_params.get('include_drafts', 'false').lower() == 'true'
        
        if not website_id:
            return Response(
                {'error': 'website_id requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(
            page__website_id=website_id,
            exclude_from_sitemap=False
        )
        
        # Filtrer par statut si nécessaire
        if not include_drafts:
            # Utiliser try/except au cas où workflow_status n'existe pas
            try:
                queryset = queryset.filter(page__workflow_status__status='published')
            except:
                # Fallback si pas de workflow
                pass
        
        sitemap_data = []
        for page_seo in queryset:
            sitemap_data.append({
                'url_path': page_seo.page.url_path,
                'title': page_seo.page.title,
                'priority': page_seo.sitemap_priority,
                'changefreq': page_seo.sitemap_changefreq,
                'last_modified': page_seo.updated_at
            })
        
        serializer = PageSitemapSerializer(sitemap_data, many=True)
        
        return Response({
            'website_id': int(website_id),
            'total_pages': len(sitemap_data),
            'include_drafts': include_drafts,
            'pages': serializer.data
        })

class PagePerformanceViewSet(PageSeoBaseViewSet):
    """
    ViewSet pour performance des pages
    """
    
    serializer_class = PagePerformanceSerializer
    http_method_names = ['get', 'post']  # Pas de création/update directe
    
    def get_queryset(self):
        # 🎯 Le mixin gère le filtrage automatiquement
        return PagePerformance.objects.select_related(
            'page',
            'page__website',
            'page__website__brand'
        )
    
    @action(detail=False, methods=['post'])
    def regenerate(self, request):
        """Forcer la régénération de pages"""
        page_ids = request.data.get('page_ids', [])
        
        if not page_ids:
            return Response(
                {'error': 'page_ids requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Marquer comme nécessitant régénération
        performances = self.get_queryset().filter(page_id__in=page_ids)
        updated_count = 0
        
        for performance in performances:
            performance.last_rendered_at = None
            performance.save(update_fields=['last_rendered_at'])
            updated_count += 1
        
        return Response({
            'message': f'{updated_count} pages marquées pour régénération',
            'updated_count': updated_count
        })