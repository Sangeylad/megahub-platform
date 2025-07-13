# backend/blog_collections/serializers/collection_serializers.py

from rest_framework import serializers
from django.db import transaction
from common.serializers.mixins import TimestampedSerializer, BrandScopedSerializer
from common.serializers.mixins import StatsMixin, SlugMixin
from ..models import BlogCollection, BlogCollectionItem


class BlogCollectionItemSerializer(TimestampedSerializer):
    """Item de collection avec navigation"""
    
    # Champs article read-only
    article_title = serializers.CharField(source='article.page.title', read_only=True)
    article_url = serializers.CharField(source='article.page.url_path', read_only=True)
    article_author = serializers.CharField(source='article.primary_author.get_full_name', read_only=True)
    article_reading_time = serializers.IntegerField(source='article.reading_time_minutes', read_only=True)
    article_published_date = serializers.DateTimeField(source='article.published_date', read_only=True)
    
    # Champs calculés
    display_title = serializers.CharField(read_only=True)
    display_description = serializers.CharField(read_only=True)
    
    # Navigation
    has_next = serializers.SerializerMethodField()
    has_previous = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogCollectionItem
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_has_next(self, obj):
        """Vérifie s'il y a un article suivant"""
        return obj.get_next_item() is not None
    
    def get_has_previous(self, obj):
        """Vérifie s'il y a un article précédent"""
        return obj.get_previous_item() is not None


class BlogCollectionSerializer(TimestampedSerializer, BrandScopedSerializer, SlugMixin):
    """Collection avec stats et articles"""
    
    # Champs calculés read-only
    articles_count = serializers.IntegerField(read_only=True)
    published_articles_count = serializers.IntegerField(read_only=True)
    reading_time_total = serializers.IntegerField(read_only=True)
    
    # Relations
    template_page_title = serializers.CharField(source='template_page.title', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = BlogCollection
        fields = '__all__'
        
        # Configuration par action
        field_config = {
            'list': [
                'id', 'name', 'slug', 'collection_type', 'description',
                'cover_image_url', 'is_active', 'is_featured', 'is_sequential',
                'articles_count', 'published_articles_count', 'reading_time_total',
                'created_by_name', 'created_at'
            ],
            'detail': '__all__',
            'create': [
                'name', 'description', 'collection_type', 'template_page',
                'cover_image_url', 'is_active', 'is_featured', 'is_sequential',
                'meta_title', 'meta_description'
                # ✅ BRAND EXCLU - géré par middleware + perform_create
            ]
        }
        
        # ✅ BRAND ET CREATED_BY exclus des writes
        read_only_fields = ['created_at', 'updated_at', 'slug', 'created_by', 'brand']
    
    def _get_articles_list(self, obj):
        """Liste ordonnée des articles"""
        items = obj.collection_items.select_related(
            'article__page', 'article__primary_author'
        ).order_by('order')
        
        return [
            {
                'id': item.article.id,
                'title': item.get_display_title(),
                'author': item.article.primary_author.get_full_name(),
                'order': item.order,
                'is_optional': item.is_optional,
                'is_bonus': item.is_bonus,
                'reading_time': item.article.reading_time_minutes,
                'url_path': item.article.page.url_path
            }
            for item in items
        ]
    
    def _get_navigation_structure(self, obj):
        """Structure de navigation complète"""
        items = obj.get_articles_ordered()
        structure = []
        
        for i, article in enumerate(items):
            structure.append({
                'position': i + 1,
                'article_id': article.id,
                'title': article.page.title,
                'has_previous': i > 0,
                'has_next': i < len(items) - 1
            })
        
        return structure
    
    def create(self, validated_data):
        """Création avec created_by automatique"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class BlogCollectionManagementSerializer(serializers.Serializer):
    """Serializer pour gestion en masse des collections"""
    
    collection_id = serializers.IntegerField()
    article_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="IDs des articles à ajouter/réorganiser"
    )
    action = serializers.ChoiceField(
        choices=[
            ('add', 'Ajouter articles'),
            ('remove', 'Retirer articles'),
            ('reorder', 'Réorganiser ordre')
        ]
    )
    
    def validate(self, attrs):
        """Validation de l'action de gestion"""
        collection_id = attrs['collection_id']
        article_ids = attrs['article_ids']
        
        # Vérifier existence collection
        try:
            collection = BlogCollection.objects.get(id=collection_id)
        except BlogCollection.DoesNotExist:
            raise serializers.ValidationError({
                'collection_id': 'Collection non trouvée'
            })
        
        # Vérifier brand access
        request = self.context.get('request')
        if request and hasattr(request, 'current_brand'):
            if collection.brand != request.current_brand:
                raise serializers.ValidationError({
                    'collection_id': 'Accès refusé à cette collection'
                })
        
        attrs['collection'] = collection
        return attrs
    
    @transaction.atomic
    def save(self):
        """Exécute l'action de gestion"""
        collection = self.validated_data['collection']
        article_ids = self.validated_data['article_ids']
        action = self.validated_data['action']
        user = self.context['request'].user
        
        if action == 'add':
            return self._add_articles(collection, article_ids, user)
        elif action == 'remove':
            return self._remove_articles(collection, article_ids)
        elif action == 'reorder':
            return self._reorder_articles(collection, article_ids)
    
    def _add_articles(self, collection, article_ids, user):
        """Ajoute des articles à la collection"""
        from blog_content.models import BlogArticle
        
        articles = BlogArticle.objects.filter(id__in=article_ids)
        added_count = 0
        
        for article in articles:
            item, created = BlogCollectionItem.objects.get_or_create(
                collection=collection,
                article=article,
                defaults={
                    'order': collection.articles.count(),
                    'added_by': user
                }
            )
            if created:
                added_count += 1
        
        return {'action': 'add', 'added_count': added_count}
    
    def _remove_articles(self, collection, article_ids):
        """Retire des articles de la collection"""
        removed_count = BlogCollectionItem.objects.filter(
            collection=collection,
            article_id__in=article_ids
        ).delete()[0]
        
        return {'action': 'remove', 'removed_count': removed_count}
    
    def _reorder_articles(self, collection, article_ids):
        """Réorganise l'ordre des articles"""
        for i, article_id in enumerate(article_ids):
            BlogCollectionItem.objects.filter(
                collection=collection,
                article_id=article_id
            ).update(order=i)
        
        return {'action': 'reorder', 'reordered_count': len(article_ids)}