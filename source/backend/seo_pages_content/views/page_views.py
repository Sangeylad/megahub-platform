# backend/seo_pages_content/views/page_views.py

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q

from .base_views import PageContentBaseViewSet
from ..models import Page
from ..serializers import (
    PageListSerializer,
    PageDetailSerializer,
    PageCreateSerializer,

)
from ..filters import PageFilter

class PageViewSet(PageContentBaseViewSet):
    """
    ViewSet pour gestion des pages
    
    Endpoints RESTful :
    - GET /pages/                 # Liste
    - POST /pages/                # Création
    - GET /pages/{id}/            # Détail
    - PUT /pages/{id}/            # Update
    - DELETE /pages/{id}/         # Delete
    - GET /pages/by-website/      # Pages par site
    - POST /pages/bulk-create/    # Création en masse
    """
    
    queryset = Page.objects.all()
    filterset_class = PageFilter
    search_fields = ['title', 'url_path', 'meta_description']
    ordering_fields = ['title', 'created_at', 'updated_at']
    
    def get_queryset(self):
        return super().get_queryset().select_related(
            'website',
            'website__brand'
        ).annotate(
            keywords_count=Count('page_keywords', distinct=True)
        )
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PageListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return PageCreateSerializer
        return PageDetailSerializer
    
    @action(detail=False, methods=['get'])
    def by_website(self, request):
        """Pages groupées par site web"""
        website_id = request.query_params.get('website_id')
        
        if not website_id:
            return Response(
                {'error': 'website_id requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        pages = self.get_queryset().filter(website_id=website_id)
        
        pages_by_type = {}
        for page in pages:
            page_type = page.get_page_type_display()
            if page_type not in pages_by_type:
                pages_by_type[page_type] = []
            
            pages_by_type[page_type].append({
                'id': page.id,
                'title': page.title,
                'url_path': page.url_path,
                'keywords_count': page.keywords_count
            })
        
        return Response({
            'website_id': int(website_id),
            'total_pages': pages.count(),
            'pages_by_type': pages_by_type
        })
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Création en masse de pages"""
        pages_data = request.data.get('pages', [])
        
        if not pages_data:
            return Response(
                {'error': 'pages requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_pages = []
        errors = []
        
        for page_data in pages_data:
            serializer = PageCreateSerializer(data=page_data)
            if serializer.is_valid():
                page = serializer.save()
                created_pages.append({
                    'id': page.id,
                    'title': page.title,
                    'url_path': page.url_path
                })
            else:
                errors.append({
                    'data': page_data,
                    'errors': serializer.errors
                })
        
        return Response({
            'created': len(created_pages),
            'errors': len(errors),
            'created_pages': created_pages,
            'validation_errors': errors
        })

