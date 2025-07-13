# backend/seo_pages_keywords/views/keyword_views.py

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Sum, Avg, Q
from django.db import transaction

from .base_views import PageKeywordsBaseViewSet
from ..models import PageKeyword
from ..serializers import (
    PageKeywordListSerializer,
    PageKeywordDetailSerializer,
    PageKeywordCreateSerializer,
    PageKeywordBulkCreateSerializer,
    PageKeywordStatsSerializer
)

class PageKeywordViewSet(PageKeywordsBaseViewSet):
    """
    ViewSet pour associations page-keyword
    
    Endpoints RESTful :
    - GET /page-keywords/         # Liste
    - POST /page-keywords/        # Création
    - GET /page-keywords/{id}/    # Détail
    - PUT /page-keywords/{id}/    # Update
    - DELETE /page-keywords/{id}/ # Delete
    - POST /page-keywords/bulk-create/ # Création en masse
    - GET /page-keywords/stats/   # Statistiques
    """
    
    queryset = PageKeyword.objects.all()
    
    filterset_fields = ['page', 'keyword_type', 'is_ai_selected', 'source_cocoon']
    search_fields = ['keyword__keyword', 'page__title']
    
    def get_queryset(self):
        # 🔧 FIX: Utiliser le mixin BrandScopedViewSetMixin qui gère déjà le filtrage
        return super().get_queryset().select_related(
            'page',
            'page__website', 
            'page__website__brand',
            'keyword',
            'source_cocoon'
        )
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PageKeywordListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return PageKeywordCreateSerializer
        return PageKeywordDetailSerializer
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Création en masse d'associations page-keyword"""
        serializer = PageKeywordBulkCreateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        page_id = serializer.validated_data['page']
        keywords_data = serializer.validated_data['keywords']
        
        created_associations = []
        errors = []
        
        with transaction.atomic():
            for keyword_data in keywords_data:
                try:
                    association = PageKeyword.objects.create(
                        page_id=page_id,
                        keyword_id=keyword_data['keyword_id'],
                        keyword_type=keyword_data['keyword_type'],
                        position=keyword_data.get('position'),
                        source_cocoon_id=keyword_data.get('source_cocoon_id'),
                        is_ai_selected=keyword_data.get('is_ai_selected', False),
                        notes=keyword_data.get('notes', '')
                    )
                    
                    created_associations.append({
                        'id': association.id,
                        'keyword_id': association.keyword.id,
                        'keyword_text': association.keyword.keyword,
                        'keyword_type': association.keyword_type
                    })
                    
                except Exception as e:
                    errors.append({
                        'keyword_data': keyword_data,
                        'error': str(e)
                    })
        
        return Response({
            'created_count': len(created_associations),
            'error_count': len(errors),
            'created_associations': created_associations,
            'errors': errors
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Statistiques des associations par page"""
        page_id = request.query_params.get('page_id')
        website_id = request.query_params.get('website_id')
        
        queryset = self.get_queryset()
        
        if page_id:
            queryset = queryset.filter(page_id=page_id)
        elif website_id:
            queryset = queryset.filter(page__website_id=website_id)
        
        # Stats globales
        total_stats = queryset.aggregate(
            total_keywords=Count('id'),
            total_volume=Sum('keyword__volume'),
            avg_volume=Avg('keyword__volume')
        )
        
        # Stats par type
        type_stats = queryset.values('keyword_type').annotate(
            count=Count('id'),
            total_volume=Sum('keyword__volume')
        )
        
        # Stats par page si website
        if website_id and not page_id:
            page_stats = queryset.values(
                'page_id',
                'page__title'
            ).annotate(
                total_keywords=Count('id'),
                primary_keywords=Count('id', filter=Q(keyword_type='primary')),
                secondary_keywords=Count('id', filter=Q(keyword_type='secondary')),
                anchor_keywords=Count('id', filter=Q(keyword_type='anchor')),
                ai_selected_count=Count('id', filter=Q(is_ai_selected=True)),
                total_volume=Sum('keyword__volume'),
                avg_volume=Avg('keyword__volume')
            ).order_by('-total_keywords')
            
            # Cocons utilisés par page
            for page_stat in page_stats:
                page_cocoons = queryset.filter(
                    page_id=page_stat['page_id'],
                    source_cocoon__isnull=False
                ).values_list('source_cocoon__name', flat=True).distinct()
                page_stat['cocoons_used'] = list(page_cocoons)
            
            page_stats_serializer = PageKeywordStatsSerializer(page_stats, many=True)
            
            return Response({
                'website_id': int(website_id),
                'global_stats': total_stats,
                'stats_by_type': {item['keyword_type']: item for item in type_stats},
                'stats_by_page': page_stats_serializer.data
            })
        
        return Response({
            'page_id': page_id,
            'global_stats': total_stats,
            'stats_by_type': {item['keyword_type']: item for item in type_stats}
        })
