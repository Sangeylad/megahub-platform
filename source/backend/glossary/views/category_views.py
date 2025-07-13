# backend/glossary/views/category_views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Q, Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from glossary.models import TermCategory
from glossary.serializers import (
    TermCategorySerializer, 
    TermCategoryListSerializer,
    TermCategoryTreeSerializer
)
from glossary.throttling import GlossaryReadThrottle, GlossaryStatsThrottle


class TermCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour les catégories de termes - API publique WordPress
    
    Endpoints disponibles:
    - GET /glossaire/categories/ - Liste des catégories
    - GET /glossaire/categories/{id}/ - Détail d'une catégorie
    - GET /glossaire/categories/tree/ - Arbre hiérarchique
    - GET /glossaire/categories/by-slug/{slug}/ - Recherche par slug
    """
    
    queryset = TermCategory.objects.filter(is_active=True).select_related('parent').prefetch_related('children')
    permission_classes = [AllowAny]
    throttle_classes = [GlossaryReadThrottle]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'order', 'created_at']
    ordering = ['order', 'name']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TermCategoryListSerializer
        elif self.action == 'tree':
            return TermCategoryTreeSerializer
        return TermCategorySerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtres par paramètres GET
        parent_id = self.request.query_params.get('parent')
        level = self.request.query_params.get('level')
        has_terms = self.request.query_params.get('has_terms')
        
        if parent_id is not None:
            if parent_id == 'null' or parent_id == '':
                queryset = queryset.filter(parent=None)
            else:
                queryset = queryset.filter(parent_id=parent_id)
        
        if level is not None:
            # Filtrer par niveau hiérarchique
            try:
                level = int(level)
                if level == 0:
                    queryset = queryset.filter(parent=None)
                elif level == 1:
                    queryset = queryset.filter(parent__isnull=False, parent__parent=None)
                elif level == 2:
                    queryset = queryset.filter(parent__parent__isnull=False)
            except ValueError:
                pass
        
        if has_terms == 'true':
            queryset = queryset.annotate(
                active_terms_count=Count('terms', filter=Q(terms__is_active=True))
            ).filter(active_terms_count__gt=0)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """
        Retourne l'arbre hiérarchique complet des catégories
        GET /glossaire/categories/tree/
        """
        root_categories = self.get_queryset().filter(parent=None)
        serializer = TermCategoryTreeSerializer(root_categories, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='by-slug/(?P<slug>[^/.]+)')
    def by_slug(self, request, slug=None):
        """
        Récupère une catégorie par son slug
        GET /glossaire/categories/by-slug/marketing/
        """
        try:
            category = self.get_queryset().get(slug=slug)
            serializer = self.get_serializer(category)
            return Response(serializer.data)
        except TermCategory.DoesNotExist:
            return Response(
                {'error': 'Catégorie non trouvée'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def breadcrumb(self, request, pk=None):
        """
        Retourne le fil d'Ariane pour une catégorie
        GET /glossaire/categories/{id}/breadcrumb/
        """
        category = self.get_object()
        breadcrumb = list(category.get_ancestors()) + [category]
        serializer = TermCategoryListSerializer(breadcrumb, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Statistiques globales des catégories - Throttling plus strict
        GET /glossaire/categories/stats/
        """
        # Override le throttling pour cette action coûteuse
        self.throttle_classes = [GlossaryStatsThrottle]
        
        queryset = self.get_queryset()
        
        stats = {
            'total_categories': queryset.count(),
            'root_categories': queryset.filter(parent=None).count(),
            'categories_with_terms': queryset.annotate(
                terms_count=Count('terms', filter=Q(terms__is_active=True))
            ).filter(terms_count__gt=0).count(),
            'max_level': 0
        }
        
        # Calculer le niveau maximum
        for category in queryset:
            level = category.get_level()
            if level > stats['max_level']:
                stats['max_level'] = level
        
        return Response(stats)