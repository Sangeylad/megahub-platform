# backend/seo_pages_hierarchy/views/hierarchy_views.py

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.db import transaction
import logging

from .base_views import PageHierarchyBaseViewSet
from ..models import PageHierarchy, PageBreadcrumb
from ..serializers import (
    PageHierarchySerializer,
    PageHierarchyCreateSerializer,
    PageHierarchyTreeSerializer,
    PageBreadcrumbSerializer
)

logger = logging.getLogger(__name__)

class PageHierarchyViewSet(PageHierarchyBaseViewSet):
    """
    ViewSet pour hiérarchie des pages
    
    Endpoints RESTful :
    - GET /hierarchy/              # Liste
    - POST /hierarchy/             # Création
    - GET /hierarchy/{id}/         # Détail
    - PUT /hierarchy/{id}/         # Update
    - DELETE /hierarchy/{id}/      # Delete
    - GET /hierarchy/tree/         # Arbre complet
    - POST /hierarchy/rebuild/     # Reconstruction
    """
    
    serializer_class = PageHierarchySerializer
    
    def get_queryset(self):
        # Le BrandScopedViewSetMixin s'occupe du filtrage automatiquement
        return PageHierarchy.objects.select_related(
            'page',
            'page__website',
            'page__website__brand',
            'parent'
        )
    
    def get_serializer_class(self):
        """Utiliser serializer robuste pour création"""
        if self.action == 'create':
            return PageHierarchyCreateSerializer
        elif self.action == 'tree':
            return PageHierarchyTreeSerializer
        return PageHierarchySerializer
    
    def create(self, request, *args, **kwargs):
        """Override pour gestion gracieuse des contraintes d'unicité"""
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Erreur création hiérarchie: {str(e)}")
            
            # Si contrainte d'unicité, essayer de récupérer l'existant
            page_id = request.data.get('page')
            if page_id:
                try:
                    existing = PageHierarchy.objects.get(page_id=page_id)
                    serializer = self.get_serializer(existing)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                except PageHierarchy.DoesNotExist:
                    pass
            
            return Response(
                {'error': f'Erreur création: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def perform_create(self, serializer):
        """Auto-création du breadcrumb après création hiérarchie"""
        try:
            hierarchy = serializer.save()
            
            # Créer/mettre à jour le breadcrumb
            breadcrumb, created = PageBreadcrumb.objects.get_or_create(
                page=hierarchy.page
            )
            breadcrumb.regenerate_breadcrumb()
            
        except Exception as e:
            logger.error(f"Erreur perform_create hierarchy: {str(e)}")
            raise
    
    def perform_update(self, serializer):
        """Régénération breadcrumb après update"""
        try:
            hierarchy = serializer.save()
            
            try:
                breadcrumb = hierarchy.page.breadcrumb_cache
                breadcrumb.regenerate_breadcrumb()
            except PageBreadcrumb.DoesNotExist:
                PageBreadcrumb.objects.create(page=hierarchy.page).regenerate_breadcrumb()
                
        except Exception as e:
            logger.error(f"Erreur perform_update hierarchy: {str(e)}")
            raise
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Arbre hiérarchique complet par website"""
        website_id = request.query_params.get('website_id')
        
        if not website_id:
            return Response(
                {'error': 'website_id requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Récupérer pages racines (sans parent)
            root_hierarchies = self.get_queryset().filter(
                page__website_id=website_id,
                parent__isnull=True
            )
            
            serializer = PageHierarchyTreeSerializer(root_hierarchies, many=True)
            
            return Response({
                'website_id': int(website_id),
                'tree': serializer.data
            })
            
        except Exception as e:
            logger.error(f"Erreur tree pour website {website_id}: {str(e)}")
            return Response(
                {'error': f'Erreur lors de la récupération de l\'arbre: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def rebuild(self, request):
        """Reconstruction complète des breadcrumbs"""
        website_id = request.data.get('website_id')
        
        if not website_id:
            return Response(
                {'error': 'website_id requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                # Régénérer tous les breadcrumbs du site
                hierarchies = self.get_queryset().filter(page__website_id=website_id)
                rebuilt_count = 0
                
                for hierarchy in hierarchies:
                    breadcrumb, created = PageBreadcrumb.objects.get_or_create(
                        page=hierarchy.page
                    )
                    breadcrumb.regenerate_breadcrumb()
                    rebuilt_count += 1
            
            return Response({
                'message': f'{rebuilt_count} breadcrumbs reconstruits',
                'website_id': int(website_id),
                'rebuilt_count': rebuilt_count
            })
            
        except Exception as e:
            logger.error(f"Erreur rebuild pour website {website_id}: {str(e)}")
            return Response(
                {'error': f'Erreur lors de la reconstruction: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def move(self, request, pk=None):
        """Déplacer une page dans la hiérarchie"""
        hierarchy = self.get_object()
        new_parent_id = request.data.get('parent_id')
        
        try:
            with transaction.atomic():
                if new_parent_id:
                    # Vérifier que le nouveau parent existe et n'est pas un descendant
                    try:
                        new_parent = PageHierarchy.objects.get(id=new_parent_id)
                        
                        # Vérifier relation circulaire
                        current = new_parent
                        depth = 0
                        while current.parent and depth < 10:
                            if current.parent.page == hierarchy.page:
                                return Response(
                                    {'error': 'Relation circulaire détectée'},
                                    status=status.HTTP_400_BAD_REQUEST
                                )
                            current = current.parent
                            depth += 1
                        
                        hierarchy.parent = new_parent.page
                        
                    except PageHierarchy.DoesNotExist:
                        return Response(
                            {'error': 'Parent non trouvé'},
                            status=status.HTTP_404_NOT_FOUND
                        )
                else:
                    hierarchy.parent = None
                
                hierarchy.save(update_fields=['parent'])
                
                # Régénérer les breadcrumbs
                breadcrumb, created = PageBreadcrumb.objects.get_or_create(
                    page=hierarchy.page
                )
                breadcrumb.regenerate_breadcrumb()
            
            serializer = self.get_serializer(hierarchy)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Erreur move hierarchy {pk}: {str(e)}")
            return Response(
                {'error': f'Erreur lors du déplacement: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PageBreadcrumbViewSet(PageHierarchyBaseViewSet):
    """
    ViewSet pour breadcrumbs
    
    Endpoints RESTful :
    - GET /breadcrumbs/           # Liste
    - GET /breadcrumbs/{id}/      # Détail
    - POST /breadcrumbs/{id}/regenerate/ # Régénération
    """
    
    serializer_class = PageBreadcrumbSerializer
    
    def get_queryset(self):
        # Le filtrage brand se fait automatiquement via le mixin
        return PageBreadcrumb.objects.select_related(
            'page',
            'page__website',
            'page__website__brand'
        )
    
    @action(detail=True, methods=['post'])
    def regenerate(self, request, pk=None):
        """Régénération du breadcrumb"""
        breadcrumb = self.get_object()
        
        try:
            new_breadcrumb = breadcrumb.regenerate_breadcrumb()
            
            return Response({
                'message': 'Breadcrumb régénéré',
                'page_title': breadcrumb.page.title,
                'breadcrumb': new_breadcrumb
            })
            
        except Exception as e:
            logger.error(f"Erreur regenerate breadcrumb {pk}: {str(e)}")
            return Response(
                {'error': f'Erreur lors de la régénération: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def bulk_regenerate(self, request):
        """Régénération en masse des breadcrumbs"""
        page_ids = request.data.get('page_ids', [])
        
        if not page_ids:
            return Response(
                {'error': 'page_ids requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            regenerated_count = 0
            errors = []
            
            for page_id in page_ids:
                try:
                    breadcrumb, created = PageBreadcrumb.objects.get_or_create(
                        page_id=page_id
                    )
                    breadcrumb.regenerate_breadcrumb()
                    regenerated_count += 1
                except Exception as e:
                    errors.append({
                        'page_id': page_id,
                        'error': str(e)
                    })
            
            return Response({
                'regenerated_count': regenerated_count,
                'total_requested': len(page_ids),
                'errors': errors
            })
            
        except Exception as e:
            logger.error(f"Erreur bulk regenerate: {str(e)}")
            return Response(
                {'error': f'Erreur lors de la régénération en masse: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )