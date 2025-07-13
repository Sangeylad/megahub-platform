# backend/blog_content/serializers/content_serializers.py

from rest_framework import serializers
from django.db import transaction
from common.serializers.mixins import TimestampedSerializer
from common.serializers.mixins import StatsMixin, SlugMixin
from seo_pages_content.models import Page
from ..models import BlogArticle, BlogAuthor, BlogTag


class BlogAuthorSerializer(TimestampedSerializer, StatsMixin):
    """Auteur blog - version content pure"""
    
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = BlogAuthor
        fields = '__all__'
        
        field_config = {
            'list': [
                'id', 'username', 'display_name', 'full_name', 'avatar_url',
                'articles_count', 'expertise_topics'
            ],
            'detail': '__all__'
        }
        
        stats_fields = {
            'published_articles_count': '_get_published_count'
        }
        
        read_only_fields = ['created_at', 'updated_at', 'articles_count', 'user']
    
    def _get_published_count(self, obj):
        return obj.blog_articles.filter(
            publishing_status__status='published'  # ✅ Via la relation publishing_status
        ).count()


class BlogTagSerializer(TimestampedSerializer, SlugMixin, StatsMixin):
    """Tag blog avec auto-slug"""
    
    class Meta:
        model = BlogTag
        fields = '__all__'
        
        field_config = {
            'list': ['id', 'name', 'slug', 'color', 'usage_count'],
            'detail': '__all__'
        }
        
        slug_field = 'slug'
        slug_source_field = 'name'
        
        stats_fields = {
            'articles_count': '_get_articles_count'
        }
        
        read_only_fields = ['created_at', 'updated_at', 'usage_count', 'slug']
    
    def _get_articles_count(self, obj):
        return obj.blog_articles.filter(
            publishing_status__status='published'  # ✅ Via la relation publishing_status
        ).count()


class BlogArticleSerializer(TimestampedSerializer, StatsMixin):
    """Article blog - version content pure"""
    
    # Champs Page read-only
    page_title = serializers.CharField(source='page.title', read_only=True)
    page_url_path = serializers.CharField(source='page.url_path', read_only=True)
    page_status = serializers.CharField(source='page.status', read_only=True)
    website_name = serializers.CharField(source='page.website.name', read_only=True)
    website_id = serializers.IntegerField(source='page.website.id', read_only=True)
    
    # ✅ NOUVEAUX CHAMPS PUBLISHING STATUS
    publishing_status = serializers.CharField(
        source='publishing_status.status', 
        read_only=True, 
        default='draft'
    )
    publishing_status_display = serializers.CharField(
        source='publishing_status.get_status_display', 
        read_only=True,
        default='Brouillon'
    )
    published_date = serializers.DateTimeField(
        source='publishing_status.published_date', 
        read_only=True
    )
    scheduled_date = serializers.DateTimeField(
        source='publishing_status.scheduled_date', 
        read_only=True
    )
    is_featured = serializers.BooleanField(
        source='publishing_status.is_featured', 
        read_only=True,
        default=False
    )
    is_published = serializers.BooleanField(
        source='publishing_status.is_published', 
        read_only=True
    )
    
    # Champs Author read-only (existants)
    author_name = serializers.CharField(source='primary_author.get_full_name', read_only=True)
    author_avatar = serializers.CharField(source='primary_author.avatar_url', read_only=True)
    
    # Champs calculés
    auto_excerpt = serializers.CharField(source='get_auto_excerpt', read_only=True)
    category_name = serializers.CharField(source='page.parent.title', read_only=True, allow_null=True)
    
    # Relations sérialisées pour détail
    primary_author = BlogAuthorSerializer(read_only=True)
    co_authors = BlogAuthorSerializer(many=True, read_only=True)
    tags = BlogTagSerializer(many=True, read_only=True)
    
    class Meta:
        model = BlogArticle
        fields = '__all__'
        
        field_config = {
            'list': [
                'id', 'page_title', 'page_url_path', 'page_status',
                'website_name', 'website_id',
                'author_name', 'author_avatar', 'category_name',
                'excerpt', 'auto_excerpt', 'featured_image_url',
                'reading_time_minutes', 'word_count', 'created_at',
                # ✅ AJOUT DES NOUVEAUX CHAMPS
                'publishing_status', 'publishing_status_display', 
                'published_date', 'is_featured', 'is_published'
            ],
            'detail': '__all__'
        }
        
        stats_fields = {
            'tags_list': '_get_tags_list',
            'category_detail': '_get_category_detail'
        }
        
        read_only_fields = ['created_at', 'updated_at', 'word_count', 'reading_time_minutes']
    
    def _get_tags_list(self, obj):
        return [
            {'id': tag.id, 'name': tag.name, 'color': tag.color}
            for tag in obj.tags.all()[:5]
        ]
    
    def _get_category_detail(self, obj):
        category = obj.get_category()
        if category:
            return {
                'id': category.id,
                'title': category.title,
                'url_path': category.url_path
            }
        return None


class BlogArticleCreateSerializer(serializers.ModelSerializer):
    """Serializer pour création d'article avec page automatique"""
    
    # Champs de la Page à créer
    title = serializers.CharField(max_length=255, help_text="Titre de l'article")
    url_path = serializers.CharField(
        max_length=500, 
        required=False, 
        allow_blank=True,
        help_text="URL de l'article (auto-généré si vide)"
    )
    meta_description = serializers.CharField(
        required=False, 
        allow_blank=True,
        help_text="Description SEO (160 caractères max)"
    )
    website_id = serializers.IntegerField(help_text="ID du website")
    
    # Relations optionnelles
    co_authors = serializers.PrimaryKeyRelatedField(
        queryset=BlogAuthor.objects.all(),
        many=True,
        required=False
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=BlogTag.objects.all(),
        many=True,
        required=False
    )
    
    class Meta:
        model = BlogArticle
        fields = [
            # Champs Page
            'title', 'url_path', 'meta_description', 'website_id',
            # Champs BlogArticle
            'primary_author', 'co_authors', 'excerpt',
            'featured_image_url', 'featured_image_alt', 'featured_image_caption',
            'tags', 'focus_keyword'
        ]
    
    def validate_title(self, value):
        """Validation titre minimum 3 caractères"""
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Le titre doit contenir au moins 3 caractères")
        return value.strip()
    
    def validate_meta_description(self, value):
        """Validation meta description max 160 caractères"""
        if value and len(value) > 160:
            raise serializers.ValidationError("La meta description ne doit pas dépasser 160 caractères")
        return value
    
    def validate_url_path(self, value):
        """Normalisation URL avec /"""
        if value and not value.startswith('/'):
            value = f"/{value}"
        return value
    
    def validate(self, data):
        """Validation globale et vérification unicité URL"""
        website_id = data.get('website_id')
        url_path = data.get('url_path', '')
        
        # Si pas d'URL, elle sera générée depuis le titre
        if not url_path:
            from django.utils.text import slugify
            url_path = f"/{slugify(data['title'])}"
            data['url_path'] = url_path
        
        # Vérifier unicité URL sur ce website
        if Page.objects.filter(website_id=website_id, url_path=url_path).exists():
            raise serializers.ValidationError({
                'url_path': f"L'URL '{url_path}' existe déjà sur ce site"
            })
        
        return data
    
    @transaction.atomic
    def create(self, validated_data):
        """Création atomique Page + BlogArticle + PublishingStatus"""
        # Extraire les champs Page
        page_data = {
            'title': validated_data.pop('title'),
            'url_path': validated_data.pop('url_path'),
            'meta_description': validated_data.pop('meta_description', ''),
            'website_id': validated_data.pop('website_id'),
            'page_type': 'blog',  # Type automatique
            'search_intent': 'TOFU'  # Par défaut, modifiable après
        }
        
        # Extraire les relations M2M
        co_authors = validated_data.pop('co_authors', [])
        tags = validated_data.pop('tags', [])
        
        # 1. Créer la Page
        page = Page.objects.create(**page_data)
        
        # 2. Créer l'Article
        article = BlogArticle.objects.create(
            page=page,
            **validated_data
        )
        
        # 3. Ajouter les relations M2M
        if co_authors:
            article.co_authors.set(co_authors)
        if tags:
            article.tags.set(tags)
        
        # 4. Créer le statut de publication par défaut
        from blog_publishing.models import BlogPublishingStatus
        BlogPublishingStatus.objects.create(
            article=article,
            status='draft'  # Par défaut en brouillon
        )
        
        # 5. Mettre à jour les compteurs
        article.primary_author.update_articles_count()
        for tag in tags:
            tag.update_usage_count()
        
        return article
    
    
    
    def to_representation(self, instance):
        """Retourner la représentation complète après création"""
        return BlogArticleSerializer(instance).data