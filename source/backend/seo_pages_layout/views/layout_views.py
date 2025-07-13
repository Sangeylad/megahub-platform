# backend/seo_pages_layout/views/layout_views.py

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils import timezone
import logging

from .base_views import PageLayoutBaseViewSet
from ..models import PageLayout, PageSection
from ..serializers import (
    PageLayoutSerializer,
    PageSectionListSerializer,
    PageSectionDetailSerializer,
    PageSectionCreateSerializer,
    PageRenderDataSerializer
)

logger = logging.getLogger(__name__)

class PageLayoutViewSet(PageLayoutBaseViewSet):
    """
    ViewSet pour configurations de layout des pages
    
    Endpoints RESTful :
    - GET /layouts/               # Liste
    - GET /layouts/{id}/          # Détail
    - PUT /layouts/{id}/          # Update
    - GET /layouts/render-data/   # Données pour Next.js
    """
    
    serializer_class = PageLayoutSerializer
    filterset_fields = ['render_strategy', 'page__website']
    
    def get_queryset(self):
        return PageLayout.objects.select_related(
            'page',
            'page__website',
            'page__website__brand',
            'created_by'
        )
    
    @action(detail=False, methods=['get'])
    def render_data(self, request):
        """Données de rendu pour Next.js"""
        page_id = request.query_params.get('page_id')
        
        if not page_id:
            return Response(
                {'error': 'page_id requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Récupérer ou créer la configuration layout
            layout, created = PageLayout.objects.get_or_create(
                page_id=page_id,
                defaults={
                    'render_strategy': 'sections',
                    'created_by': request.user
                }
            )
            
            # Récupérer les sections avec hiérarchie
            sections = PageSection.objects.filter(
                page_id=page_id,
                is_active=True,
                parent_section__isnull=True  # Sections racines seulement
            ).select_related('created_by').prefetch_related(
                'child_sections'
            ).order_by('order')
            
            # Sérialiser les données
            layout_data = PageLayoutSerializer(layout).data
            
            # Ajouter les sections avec hiérarchie
            sections_data = []
            for section in sections:
                section_data = PageSectionDetailSerializer(section).data
                
                # Ajouter les enfants si container
                if section.section_type.startswith('layout_'):
                    children = section.child_sections.filter(
                        is_active=True
                    ).order_by('order')
                    section_data['children'] = PageSectionListSerializer(children, many=True).data
                
                sections_data.append(section_data)
            
            layout_data['sections'] = sections_data
            
            return Response(layout_data)
            
        except Exception as e:
            logger.error(f"Erreur render_data pour page {page_id}: {str(e)}")
            return Response(
                {'error': f'Erreur lors de la récupération des données: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PageSectionViewSet(PageLayoutBaseViewSet):
    """
    ViewSet pour sections du page builder
    
    Endpoints RESTful :
    - GET /sections/              # Liste
    - POST /sections/             # Création
    - GET /sections/{id}/         # Détail
    - PUT /sections/{id}/         # Update
    - DELETE /sections/{id}/      # Suppression
    - POST /sections/reorder/     # Réorganisation
    - POST /sections/{id}/duplicate/  # Duplication
    """
    
    serializer_class = PageSectionListSerializer
    filterset_fields = ['page', 'section_type', 'parent_section', 'is_active']
    
    def get_queryset(self):
        return PageSection.objects.select_related(
            'page',
            'page__website',
            'page__website__brand',
            'parent_section',
            'created_by'
        ).prefetch_related('child_sections')
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PageSectionCreateSerializer
        elif self.action == 'retrieve':
            return PageSectionDetailSerializer
        return PageSectionListSerializer
    
    def perform_create(self, serializer):
        """Override pour ajouter created_by automatiquement"""
        # 🆕 CRITIQUE : Correction de l'erreur "created_by" manquant
        serializer.save(created_by=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """Override pour gestion gracieuse des erreurs"""
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Erreur création section: {str(e)}")
            return Response(
                {'error': f'Erreur création: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def perform_update(self, serializer):
        """Override pour mettre à jour updated_at"""
        serializer.save()
    
    def perform_destroy(self, instance):
        """Soft delete au lieu de suppression physique"""
        instance.is_active = False
        instance.save(update_fields=['is_active'])
    
    @action(detail=False, methods=['post'])
    def reorder(self, request):
        """Réorganiser les sections d'une page"""
        page_id = request.data.get('page_id')
        sections_order = request.data.get('sections', [])
        
        if not page_id or not sections_order:
            return Response(
                {'error': 'page_id et sections requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        updated_count = 0
        errors = []
        
        try:
            for section_data in sections_order:
                section_id = section_data.get('id')
                new_order = section_data.get('order')
                parent_section_id = section_data.get('parent_section')
                
                try:
                    section = self.get_queryset().get(
                        id=section_id,
                        page_id=page_id
                    )
                    
                    section.order = new_order
                    if parent_section_id:
                        section.parent_section_id = parent_section_id
                    else:
                        section.parent_section = None
                    
                    section.save(update_fields=['order', 'parent_section'])
                    updated_count += 1
                    
                except PageSection.DoesNotExist:
                    errors.append({
                        'section_id': section_id,
                        'error': 'Section non trouvée'
                    })
                except Exception as e:
                    errors.append({
                        'section_id': section_id,
                        'error': str(e)
                    })
            
            return Response({
                'updated_count': updated_count,
                'total_requested': len(sections_order),
                'errors': errors
            })
            
        except Exception as e:
            logger.error(f"Erreur reorder sections: {str(e)}")
            return Response(
                {'error': f'Erreur lors de la réorganisation: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Dupliquer une section"""
        section = self.get_object()
        
        try:
            # Créer la copie
            new_section = PageSection.objects.create(
                page=section.page,
                parent_section=section.parent_section,
                section_type=section.section_type,
                data=section.data.copy() if section.data else {},
                layout_config=section.layout_config.copy() if section.layout_config else {},
                order=section.order + 1,
                is_active=True,
                version=section.version,
                created_by=request.user
            )
            
            # Dupliquer les enfants si container
            if section.section_type.startswith('layout_'):
                for child in section.child_sections.filter(is_active=True):
                    PageSection.objects.create(
                        page=child.page,
                        parent_section=new_section,
                        section_type=child.section_type,
                        data=child.data.copy() if child.data else {},
                        layout_config=child.layout_config.copy() if child.layout_config else {},
                        order=child.order,
                        is_active=True,
                        version=child.version,
                        created_by=request.user
                    )
            
            serializer = self.get_serializer(new_section)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Erreur duplication section {pk}: {str(e)}")
            return Response(
                {'error': f'Erreur lors de la duplication: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def available_types(self, request):
        """Types de sections disponibles"""
        from ..models import PageSection
        
        section_types = [
            {
                'value': choice[0],
                'label': choice[1],
                'category': 'layout' if choice[0].startswith('layout_') else 'content'
            }
            for choice in PageSection.SECTION_TYPE_CHOICES
        ]
        
        return Response({
            'section_types': section_types,
            'categories': {
                'layout': [t for t in section_types if t['category'] == 'layout'],
                'content': [t for t in section_types if t['category'] == 'content']
            }
        })