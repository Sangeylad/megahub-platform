# backend/blog_config/serializers/config_serializers.py

from rest_framework import serializers
from common.serializers.mixins import TimestampedSerializer, WebsiteScopedSerializer
from common.serializers.mixins import StatsMixin
from ..models import BlogConfig


class BlogConfigSerializer(TimestampedSerializer, StatsMixin, WebsiteScopedSerializer):
    """Configuration blog avec stats automatiques"""
    
    # Champs relationnels read-only
    website_name = serializers.CharField(source='website.name', read_only=True)
    template_article_title = serializers.CharField(
        source='template_article_page.title', 
        read_only=True
    )
    full_blog_url = serializers.CharField(read_only=True)
    
    class Meta:
        model = BlogConfig
        fields = '__all__'
        
        # Configuration par action
        field_config = {
            'list': [
                'id', 'website_name', 'blog_name', 'blog_slug',
                'posts_per_page', 'enable_comments', 'enable_newsletter',
                'total_articles', 'published_articles', 'enable_auto_publish'
            ],
            'detail': '__all__',
            'create': [
                'website', 'blog_name', 'blog_slug', 'blog_description',
                'posts_per_page', 'posts_per_rss', 'excerpt_length',
                'enable_comments', 'enable_newsletter', 'enable_related_posts',
                'enable_auto_publish', 'default_meta_title_pattern'
            ]
        }
        
        # Stats calculées
        stats_fields = {
            'total_articles': '_get_total_articles',
            'published_articles': '_get_published_articles', 
            'total_authors': '_get_total_authors'
        }
        
        read_only_fields = ['created_at', 'updated_at', 'full_blog_url']
    
    def _get_total_articles(self, obj):
        return obj.get_total_articles()
    
    def _get_published_articles(self, obj):
        return obj.get_published_articles()
    
    def _get_total_authors(self, obj):
        from blog_content.models import BlogAuthor
        return BlogAuthor.objects.filter(
            blog_articles__page__website=obj.website
        ).distinct().count()
    
    def validate_blog_slug(self, value):
        """Validation du slug blog"""
        if not value.replace('-', '').replace('_', '').isalnum():
            raise serializers.ValidationError(
                "Le slug ne peut contenir que lettres, chiffres, tirets et underscores"
            )
        return value.lower()
    
    def validate(self, attrs):
        """Validation unicité slug par website"""
        website = attrs.get('website') or self.get_website_from_context()
        blog_slug = attrs.get('blog_slug')
        
        if website and blog_slug:
            qs = BlogConfig.objects.filter(website=website, blog_slug=blog_slug)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({
                    'blog_slug': 'Ce slug existe déjà pour ce site'
                })
        
        return super().validate(attrs)
