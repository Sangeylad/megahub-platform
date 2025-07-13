# backend/seo_pages_seo/serializers/seo_serializers.py

from rest_framework import serializers

from .base_serializers import PageSeoBaseSerializer  
from ..models import PageSEO, PagePerformance

class PageSEOSerializer(PageSeoBaseSerializer):
    """Serializer configuration SEO des pages"""
    
    page_title = serializers.CharField(source='page.title', read_only=True)
    page_url = serializers.CharField(source='page.url_path', read_only=True)
    page_type = serializers.CharField(source='page.page_type', read_only=True)
    changefreq_display = serializers.CharField(source='get_sitemap_changefreq_display', read_only=True)
    
    class Meta:
        model = PageSEO
        fields = [
            'id', 'page', 'page_title', 'page_url', 'page_type',
            'featured_image', 'sitemap_priority', 'sitemap_changefreq', 'changefreq_display',
            'exclude_from_sitemap', 'created_at', 'updated_at'
        ]
    
    def validate_sitemap_priority(self, value):
        """Validation priorité sitemap"""
        if value < 0.0 or value > 1.0:
            raise serializers.ValidationError(
                "La priorité sitemap doit être entre 0.0 et 1.0"
            )
        return value
    
    def validate_featured_image(self, value):
        """Validation URL image"""
        if value and not value.startswith(('http://', 'https://')):
            raise serializers.ValidationError(
                "L'URL de l'image doit commencer par http:// ou https://"
            )
        return value

class PageSEOBulkUpdateSerializer(serializers.Serializer):
    """Serializer mise à jour en masse des configs SEO"""
    
    page_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    sitemap_priority = serializers.DecimalField(
        max_digits=2, decimal_places=1,
        required=False, min_value=0.0, max_value=1.0
    )
    sitemap_changefreq = serializers.ChoiceField(
        choices=PageSEO.CHANGEFREQ_CHOICES,
        required=False
    )
    exclude_from_sitemap = serializers.BooleanField(required=False)
    
    def validate_page_ids(self, value):
        """Validation des IDs de pages"""
        from seo_pages_content.models import Page
        
        existing_ids = Page.objects.filter(id__in=value).values_list('id', flat=True)
        missing_ids = set(value) - set(existing_ids)
        
        if missing_ids:
            raise serializers.ValidationError(
                f"Pages non trouvées : {list(missing_ids)}"
            )
        
        return value

class PagePerformanceSerializer(PageSeoBaseSerializer):
    """Serializer performance des pages"""
    
    page_title = serializers.CharField(source='page.title', read_only=True)
    page_url = serializers.CharField(source='page.url_path', read_only=True)
    needs_regeneration = serializers.SerializerMethodField()
    render_time_display = serializers.SerializerMethodField()
    
    class Meta:
        model = PagePerformance
        fields = [
            'id', 'page', 'page_title', 'page_url',
            'last_rendered_at', 'render_time_ms', 'render_time_display',
            'cache_hits', 'last_crawled_at', 'needs_regeneration'
        ]
    
    def get_needs_regeneration(self, obj):
        return obj.needs_regeneration()
    
    def get_render_time_display(self, obj):
        if not obj.render_time_ms:
            return None
        
        if obj.render_time_ms < 1000:
            return f"{obj.render_time_ms}ms"
        else:
            return f"{obj.render_time_ms / 1000:.1f}s"

class PageSitemapSerializer(serializers.Serializer):
    """Serializer données sitemap XML"""
    
    url_path = serializers.CharField()
    title = serializers.CharField()
    priority = serializers.DecimalField(max_digits=2, decimal_places=1)
    changefreq = serializers.CharField()
    last_modified = serializers.DateTimeField()
    
class SitemapGenerationSerializer(serializers.Serializer):
    """Serializer génération sitemap"""
    
    website_id = serializers.IntegerField()
    include_drafts = serializers.BooleanField(default=False)
    
    def validate_website_id(self, value):
        """Validation existence du site"""
        from seo_websites_core.models import Website
        
        try:
            Website.objects.get(id=value)
        except Website.DoesNotExist:
            raise serializers.ValidationError("Site web non trouvé")
        
        return value
