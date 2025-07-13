# backend/seo_pages_content/serializers/page_serializers.py

from rest_framework import serializers

from .base_serializers import PageContentBaseSerializer
from ..models import Page

class PageListSerializer(PageContentBaseSerializer):
    """Serializer pour liste des pages - Données minimales"""
    
    website_name = serializers.CharField(source='website.name', read_only=True)
    page_type_display = serializers.CharField(source='get_page_type_display', read_only=True)
    search_intent_display = serializers.CharField(source='get_search_intent_display', read_only=True)
    
    class Meta:
        model = Page
        fields = [
            'id', 'title', 'url_path', 'website', 'website_name',
            'page_type', 'page_type_display', 'search_intent', 'search_intent_display',
            'created_at', 'updated_at'
        ]

class PageDetailSerializer(PageContentBaseSerializer):
    """Serializer détail page - Données complètes"""
    
    website_name = serializers.CharField(source='website.name', read_only=True)
    page_type_display = serializers.CharField(source='get_page_type_display', read_only=True)
    search_intent_display = serializers.CharField(source='get_search_intent_display', read_only=True)
    
    # Relations étendues (chargées si disponibles)
    hierarchy_level = serializers.SerializerMethodField()
    workflow_status = serializers.SerializerMethodField()
    keywords_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Page
        fields = [
            'id', 'title', 'url_path', 'meta_description',
            'website', 'website_name', 'page_type', 'page_type_display',
            'search_intent', 'search_intent_display',
            'hierarchy_level', 'workflow_status', 'keywords_count',
            'created_at', 'updated_at'
        ]
    
    def get_hierarchy_level(self, obj):
        try:
            return obj.hierarchy.get_level()
        except:
            return 1
    
    def get_workflow_status(self, obj):
        try:
            status = obj.workflow_status
            return {
                'status': status.status,
                'status_display': status.get_status_display(),
                'color': status.get_status_color()
            }
        except:
            return {'status': 'draft', 'status_display': 'Brouillon', 'color': '#6c757d'}
    
    def get_keywords_count(self, obj):
        return getattr(obj, 'keywords_count', 0)

class PageCreateSerializer(PageContentBaseSerializer):
    """Serializer création page - Validation stricte"""
    
    class Meta:
        model = Page
        fields = [
            'title', 'url_path', 'meta_description', 'website',
            'page_type', 'search_intent'
        ]
    
    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Le titre doit contenir au moins 3 caractères")
        return value.strip()
    
    def validate_url_path(self, value):
        if value and not value.startswith('/'):
            value = f"/{value}"
        return value
    
    def validate(self, data):
        # Vérifier unicité url_path par website
        website = data.get('website')
        url_path = data.get('url_path')
        
        if url_path and website:
            existing = Page.objects.filter(
                website=website, 
                url_path=url_path
            )
            if self.instance:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise serializers.ValidationError({
                    'url_path': 'Cette URL existe déjà sur ce site'
                })
        
        return data