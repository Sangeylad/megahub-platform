# backend/seo_websites_categorization/views/category_views.py

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from django.db import transaction

from .base_views import SeoWebsitesCategorizationBaseViewSet, WebsiteCategorizationBulkViewSet
from ..models import WebsiteCategory, WebsiteCategorization
from ..serializers import (
    WebsiteCategoryListSerializer,
    WebsiteCategoryDetailSerializer,
    WebsiteCategoryCreateSerializer,
    WebsiteCategorizationListSerializer,
    WebsiteCategorizationDetailSerializer,
    WebsiteCategorizationCreateSerializer
)
from ..filters import WebsiteCategoryFilter, WebsiteCategorizationFilter

class WebsiteCategoryViewSet(SeoWebsitesCategorizationBaseViewSet):
    """
    ViewSet pour gestion des catégories de websites
    
    Endpoints RESTful :
    - GET /categories/                    # Liste
    - POST /categories/                   # Création
    - GET /categories/{id}/               # Détail
    - PUT /categories/{id}/               # Update
    - DELETE /categories/{id}/            # Delete
    - GET /categories/tree/               # Arbre hiérarchique
    - GET /categories/stats/              # Statistiques
    - POST /categories/reorder/           # Réorganiser ordre
    """
    
    queryset = WebsiteCategory.objects.all()
    filterset_class = WebsiteCategoryFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'display_order', 'created_at']
    
    def get_queryset(self):
        # Pas de filtrage brand pour les catégories (globales)
        return self.queryset.select_related('parent').prefetch_related(
            'subcategories',
            'websites'
        ).annotate(
            websites_count=Count('websites', distinct=True),
            subcategories_count=Count('subcategories', distinct=True)
        )
    
    def get_serializer_class(self):
        if self.action == 'list':
            return WebsiteCategoryListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return WebsiteCategoryCreateSerializer
        return WebsiteCategoryDetailSerializer
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Structure hiérarchique des catégories"""
        # ✅ Utiliser le queryset annoté pour TOUTES les catégories
        all_categories = self.get_queryset()
        root_categories = all_categories.filter(parent=None)
        
        # ✅ Créer un dict pour accès rapide par ID avec annotations
        categories_dict = {cat.id: cat for cat in all_categories}
        
        def build_tree_node(category):
            return {
                'id': category.id,
                'name': category.name,
                'slug': category.slug,
                'color': category.color,
                'websites_count': getattr(category, 'websites_count', category.get_websites_count()),  # ✅ Fallback
                'subcategories_count': getattr(category, 'subcategories_count', category.get_subcategories_count()),  # ✅ Fallback
                'display_order': category.display_order,
                'children': [
                    build_tree_node(categories_dict[child.id]) 
                    for child in category.subcategories.all()
                    if child.id in categories_dict  # ✅ Sécurité
                ]
            }
        
        tree = [build_tree_node(cat) for cat in root_categories]
        
        return Response({
            'tree': tree,
            'total_categories': all_categories.count(),
            'root_categories': len(tree)
        })
    
    
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Statistiques des catégories"""
        queryset = self.get_queryset()
        
        stats = {
            'total_categories': queryset.count(),
            'root_categories': queryset.filter(parent=None).count(),
            'subcategories': queryset.filter(parent__isnull=False).count(),
            'categories_with_websites': queryset.filter(websites_count__gt=0).count(),
            'empty_categories': queryset.filter(websites_count=0).count(),
            'top_categories_by_websites': list(
                queryset.filter(websites_count__gt=0)
                .order_by('-websites_count')[:10]
                .values('id', 'name', 'websites_count')
            )
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['post'])
    def reorder(self, request):
        """Réorganiser l'ordre d'affichage des catégories"""
        categories_order = request.data.get('categories', [])
        
        if not categories_order:
            return Response(
                {'error': 'Liste categories requise'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            for item in categories_order:
                try:
                    category = WebsiteCategory.objects.get(id=item['id'])
                    category.display_order = item['display_order']
                    category.save(update_fields=['display_order'])
                except WebsiteCategory.DoesNotExist:
                    continue
        
        return Response({
            'message': f'{len(categories_order)} catégories réorganisées'
        })

class WebsiteCategorizationViewSet(WebsiteCategorizationBulkViewSet):
    """
    ViewSet pour gestion des associations Website ↔ Catégorie
    
    Endpoints RESTful :
    - GET /categorizations/                        # Liste
    - POST /categorizations/                       # Création
    - GET /categorizations/{id}/                   # Détail
    - PUT /categorizations/{id}/                   # Update
    - DELETE /categorizations/{id}/                # Delete
    - POST /categorizations/bulk-create/           # Création en masse
    - POST /categorizations/bulk-delete/           # Suppression en masse
    - GET /categorizations/by-website/             # Par website
    - GET /categorizations/by-category/            # Par catégorie
    - POST /categorizations/set-primary/           # Définir catégorie primaire
    """
    
    queryset = WebsiteCategorization.objects.all()
    filterset_class = WebsiteCategorizationFilter
    search_fields = ['website__name', 'category__name', 'notes']
    ordering_fields = ['created_at', 'is_primary', 'confidence_score']
    
    def get_queryset(self):
        # Filtrage automatique par brand via website
        return super().get_queryset().select_related(
            'website',
            'website__brand',
            'category',
            'category__parent',
            'categorized_by'
        )
    
    def get_serializer_class(self):
        if self.action == 'list':
            return WebsiteCategorizationListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return WebsiteCategorizationCreateSerializer
        return WebsiteCategorizationDetailSerializer
    
    def perform_create(self, serializer):
        """Enregistrer l'utilisateur qui fait la catégorisation"""
        serializer.save(categorized_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def by_website(self, request):
        """Catégorisations groupées par website"""
        website_id = request.query_params.get('website_id')
        
        if not website_id:
            return Response(
                {'error': 'website_id requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        categorizations = self.get_queryset().filter(website_id=website_id)
        serializer = self.get_serializer(categorizations, many=True)
        
        # ✅ FIX : Chercher directement en DB pour la primaire
        primary_categorization = categorizations.filter(is_primary=True).first()
        primary_category = None
        
        if primary_categorization:
            primary_category = {
                'category_id': primary_categorization.category.id,
                'category_name': primary_categorization.category.name,
                'category_color': primary_categorization.category.color,
                'confidence_score': primary_categorization.confidence_score
            }
        
        return Response({
            'website_id': website_id,
            'categorizations': serializer.data,
            'primary_category': primary_category  # ✅ Maintenant cohérent
        })
    
    
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Websites groupés par catégorie"""
        category_id = request.query_params.get('category_id')
        
        if not category_id:
            return Response(
                {'error': 'category_id requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        categorizations = self.get_queryset().filter(category_id=category_id)
        serializer = self.get_serializer(categorizations, many=True)
        
        return Response({
            'category_id': category_id,
            'categorizations': serializer.data,
            'total_websites': categorizations.count()
        })
    
    @action(detail=False, methods=['post'])
    def set_primary(self, request):
        """Définir une catégorie comme primaire pour un website"""
        website_id = request.data.get('website_id')
        category_id = request.data.get('category_id')
        
        if not website_id or not category_id:
            return Response(
                {'error': 'website_id et category_id requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            # Retirer le statut primaire des autres
            WebsiteCategorization.objects.filter(
                website_id=website_id
            ).update(is_primary=False)
            
            # Définir la nouvelle primaire
            categorization, created = WebsiteCategorization.objects.get_or_create(
                website_id=website_id,
                category_id=category_id,
                defaults={
                    'is_primary': True,
                    'source': 'manual',
                    'categorized_by': request.user
                }
            )
            
            if not created:
                categorization.is_primary = True
                categorization.save(update_fields=['is_primary'])
        
        return Response({
            'message': 'Catégorie primaire définie',
            'categorization_id': categorization.id
        })