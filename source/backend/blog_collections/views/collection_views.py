# backend/blog_collections/views/collection_views.py

from django.db import models
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from common.views.mixins import BrandScopedViewSetMixin, BulkActionViewSetMixin
from rest_framework.permissions import IsAuthenticated
from common.permissions.business_permissions import IsBrandMember
from ..models import BlogCollection, BlogCollectionItem
from ..serializers import (
    BlogCollectionSerializer, 
    BlogCollectionItemSerializer,
    BlogCollectionManagementSerializer
)


class BlogCollectionViewSet(BrandScopedViewSetMixin, BulkActionViewSetMixin, viewsets.ModelViewSet):
    """CRUD collections avec gestion articles"""
    queryset = BlogCollection.objects.select_related(
        'brand', 'template_page', 'created_by'
    ).prefetch_related('articles')
    
    serializer_class = BlogCollectionSerializer
    permission_classes = [IsAuthenticated, IsBrandMember]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['collection_type', 'is_active', 'is_featured', 'is_sequential']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'articles_count']
    ordering = ['-is_featured', '-created_at']
    
    def get_queryset(self):
        """Queryset avec annotations"""
        return super().get_queryset().annotate(
            articles_count=models.Count('collection_items', distinct=True),
            # ✅ VERSION SIMPLIFIÉE sans published_articles_count pour l'instant
        )
        
    
    def perform_create(self, serializer):
        """✅ VERSION PROPRE avec middleware fonctionnel"""
        user = self.request.user
        brand = getattr(self.request, 'current_brand', None)
        
        if not brand:
            raise ValidationError("Aucune brand disponible pour la création")
        
        print(f"✅ Creating collection with brand: {brand.name} (ID: {brand.id})")
        
        serializer.save(
            brand=brand,
            created_by=user 
        ) 
    
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Collections par type"""
        collection_type = request.query_params.get('type')
        if not collection_type:
            return Response({'error': 'type parameter required'}, status=400)
        
        collections = self.get_queryset().filter(collection_type=collection_type)
        page = self.paginate_queryset(collections)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def articles(self, request, pk=None):
        """Articles de la collection dans l'ordre"""
        collection = self.get_object()
        articles = collection.get_articles_ordered()
        
        # Pagination manuelle si beaucoup d'articles
        page = self.paginate_queryset(articles)
        if page is not None:
            from blog_content.serializers import BlogArticleSerializer
            serializer = BlogArticleSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        from blog_content.serializers import BlogArticleSerializer
        serializer = BlogArticleSerializer(articles, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def manage_articles(self, request, pk=None):
        """Gestion articles collection (add/remove/reorder)"""
        collection = self.get_object()
        
        # Utiliser le serializer de gestion
        data = {**request.data, 'collection_id': collection.id}
        serializer = BlogCollectionManagementSerializer(
            data=data, 
            context={'request': request}
        )
        
        if serializer.is_valid():
            result = serializer.save()
            return Response({
                'message': 'Gestion articles réussie',
                'result': result
            })
        return Response(serializer.errors, status=400)
    
    @action(detail=True, methods=['get'])
    def navigation(self, request, pk=None):
        """Structure navigation complète"""
        collection = self.get_object()
        items = collection.collection_items.select_related(
            'article', 'article__page'
        ).order_by('order')
        
        navigation = []
        for item in items:
            navigation.append({
                'item_id': item.id,
                'article_id': item.article.id,
                'title': item.get_display_title(),
                'url_path': item.article.page.url_path,
                'order': item.order,
                'is_optional': item.is_optional,
                'is_bonus': item.is_bonus,
                'has_next': item.get_next_item() is not None,
                'has_previous': item.get_previous_item() is not None
            })
        
        return Response({
            'collection': {
                'id': collection.id,
                'name': collection.name,
                'is_sequential': collection.is_sequential
            },
            'navigation': navigation,
            'total_items': len(navigation)
        })


class BlogCollectionItemViewSet(BrandScopedViewSetMixin, viewsets.ModelViewSet):
    """CRUD items collection avec navigation"""
    queryset = BlogCollectionItem.objects.select_related(
        'collection', 'article', 'article__page', 'article__primary_author', 'added_by'
    )
    serializer_class = BlogCollectionItemSerializer
    permission_classes = [IsAuthenticated, IsBrandMember]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['collection', 'is_optional', 'is_bonus']
    ordering_fields = ['order', 'created_at']
    ordering = ['order']
    
    def get_queryset(self):
        """Filtrage par collection si spécifié"""
        queryset = super().get_queryset()
        collection_id = self.request.query_params.get('collection_id')
        if collection_id:
            queryset = queryset.filter(collection_id=collection_id)
        return queryset
    
    @action(detail=True, methods=['get'])
    def next(self, request, pk=None):
        """Article suivant dans la collection"""
        item = self.get_object()
        next_item = item.get_next_item()
        
        if next_item:
            serializer = self.get_serializer(next_item)
            return Response(serializer.data)
        return Response({'message': 'Dernier article de la collection'}, status=404)
    
    @action(detail=True, methods=['get'])
    def previous(self, request, pk=None):
        """Article précédent dans la collection"""
        item = self.get_object()
        previous_item = item.get_previous_item()
        
        if previous_item:
            serializer = self.get_serializer(previous_item)
            return Response(serializer.data)
        return Response({'message': 'Premier article de la collection'}, status=404)
    
    @action(detail=False, methods=['post'])
    def reorder(self, request):
        """Réorganiser ordre des items"""
        collection_id = request.data.get('collection_id')
        items_order = request.data.get('items_order', [])  # [{'id': 1, 'order': 0}, ...]
        
        if not collection_id or not items_order:
            return Response({
                'error': 'collection_id et items_order requis'
            }, status=400)
        
        # Validation accès collection
        try:
            collection = BlogCollection.objects.get(id=collection_id)
            # Brand check fait par BrandScopedViewSetMixin
        except BlogCollection.DoesNotExist:
            return Response({'error': 'Collection non trouvée'}, status=404)
        
        # Mise à jour ordre
        updated_count = 0
        for item_data in items_order:
            updated = BlogCollectionItem.objects.filter(
                id=item_data['id'],
                collection=collection
            ).update(order=item_data['order'])
            updated_count += updated
        
        return Response({
            'message': f'{updated_count} items réorganisés',
            'updated_count': updated_count
        })