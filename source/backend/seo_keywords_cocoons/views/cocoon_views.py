# backend/seo_keywords_cocoons/views/cocoon_views.py

from rest_framework import viewsets, status, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from django.core.exceptions import ValidationError

# Local imports - 🔥 IMPORT CORRIGÉ
from ..models import SemanticCocoon, CocoonCategory
from ..serializers import (
    SemanticCocoonSerializer,
    SemanticCocoonListSerializer,
    SemanticCocoonDetailSerializer,  # 🔥 AJOUTÉ
    CocoonCategorySerializer
)
from ..filters import CocoonFilter
from ..services import CocoonStatsService

import logging
logger = logging.getLogger(__name__)

class CocoonCategoryViewSet(viewsets.ModelViewSet):
    """
    GESTION DES CATÉGORIES DE COCONS - CRUD AVEC VALIDATION
    
    Endpoints RESTful :
    - GET /seo/cocoons/categories/           # Liste
    - POST /seo/cocoons/categories/          # Création
    - GET /seo/cocoons/categories/{id}/      # Détail
    - PUT /seo/cocoons/categories/{id}/      # Update
    - DELETE /seo/cocoons/categories/{id}/   # Delete
    - GET /seo/cocoons/categories/{id}/cocoons/ # Cocons d'une catégorie
    """
    
    queryset = CocoonCategory.objects.all()
    serializer_class = CocoonCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def destroy(self, request, *args, **kwargs):
        """Suppression avec vérification des dépendances"""
        try:
            category = self.get_object()
            cocoons_count = category.cocoons.count()
            
            if cocoons_count > 0:
                logger.warning(f"Attempted to delete category {category.id} with {cocoons_count} cocoons")
                return Response(
                    {
                        'error': f'Impossible de supprimer la catégorie. '
                                f'Elle est utilisée par {cocoons_count} cocon(s).',
                        'cocoons_count': cocoons_count
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            logger.info(f"Category {category.id} ({category.name}) deleted by user {request.user.id}")
            return super().destroy(request, *args, **kwargs)
            
        except Exception as e:
            logger.error(f"Error deleting category {kwargs.get('pk')}: {e}", exc_info=True)
            return Response(
                {'error': 'Erreur lors de la suppression'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def cocoons(self, request, pk=None):
        """Liste des cocons d'une catégorie"""
        try:
            category = self.get_object()
            cocoons = category.cocoons.annotate(
                keywords_count=Count('cocoon_keywords')
            ).order_by('name')
            
            # Pagination simple
            page_size = min(int(request.query_params.get('page_size', 20)), 100)
            cocoons_list = list(cocoons[:page_size].values(
                'id', 'name', 'slug', 'keywords_count', 'created_at'
            ))
            
            return Response({
                'category': category.name,
                'cocoons': cocoons_list,
                'total': cocoons.count()
            })
            
        except Exception as e:
            logger.error(f"Error getting cocoons for category {pk}: {e}", exc_info=True)
            return Response(
                {'error': 'Erreur lors de la récupération'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class SemanticCocoonViewSet(viewsets.ModelViewSet):
    """
    GESTION DES COCONS SÉMANTIQUES - CRUD + Statistiques
    
    Endpoints RESTful :
    - GET /seo/cocoons/cocoons/               # Liste avec filtres
    - POST /seo/cocoons/cocoons/              # Création
    - GET /seo/cocoons/cocoons/{id}/          # Détail
    - PUT /seo/cocoons/cocoons/{id}/          # Update
    - DELETE /seo/cocoons/cocoons/{id}/       # Delete
    - GET /seo/cocoons/cocoons/{id}/stats/    # Statistiques détaillées
    - GET /seo/cocoons/cocoons/overview/      # Vue d'ensemble globale
    """
    
    queryset = SemanticCocoon.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CocoonFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'updated_at', 'keywords_count']
    ordering = ['name']
    
    def get_serializer_class(self):
        """Serializer par action selon pattern obligatoire"""
        serializer_map = {
            'list': SemanticCocoonListSerializer,
            'retrieve': SemanticCocoonDetailSerializer,  # 🔥 UTILISE LE BON SERIALIZER
            'overview': SemanticCocoonListSerializer,
        }
        return serializer_map.get(self.action, SemanticCocoonSerializer)
    
    def get_queryset(self):
        """Optimisation requêtes avec annotations"""
        return super().get_queryset().prefetch_related(
            'categories'
        ).annotate(
            keywords_count=Count('cocoon_keywords', distinct=True)
        ).distinct()
    
    def destroy(self, request, *args, **kwargs):
        """Suppression avec vérification et cascade"""
        try:
            cocoon = self.get_object()
            keywords_count = cocoon.cocoon_keywords.count()
            
            # Log pour audit
            logger.info(
                f"Deleting cocoon {cocoon.id} ({cocoon.name}) with {keywords_count} keywords "
                f"by user {request.user.id}"
            )
            
            # Suppression cascade automatique via ON DELETE CASCADE
            result = super().destroy(request, *args, **kwargs)
            
            logger.info(f"Cocoon {cocoon.id} successfully deleted with {keywords_count} associations")
            return result
            
        except Exception as e:
            logger.error(f"Error deleting cocoon {kwargs.get('pk')}: {e}", exc_info=True)
            return Response(
                {'error': 'Erreur lors de la suppression'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Statistiques détaillées d'un cocon via service"""
        try:
            stats = CocoonStatsService.get_cocoon_stats(int(pk))
            logger.info(f"Stats calculated for cocoon {pk} by user {request.user.id}")
            return Response(stats)
            
        except ValueError as e:
            logger.warning(f"Cocoon not found: {e}")
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error calculating stats for cocoon {pk}: {e}", exc_info=True)
            return Response(
                {'error': 'Erreur lors du calcul des statistiques'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """Vue d'ensemble de tous les cocons"""
        try:
            overview_stats = CocoonStatsService.get_cocoons_overview()
            logger.info(f"Cocoons overview requested by user {request.user.id}")
            
            return Response({
                'stats': overview_stats,
                'message': f'{overview_stats["total_cocoons"]} cocons dans la base'
            })
            
        except Exception as e:
            logger.error(f"Error getting cocoons overview: {e}", exc_info=True)
            return Response(
                {'error': 'Erreur lors de la récupération de la vue d\'ensemble'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )