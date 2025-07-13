# backend/seo_pages_layout/serializers/layout_serializers.py

from rest_framework import serializers

from .base_serializers import PageLayoutBaseSerializer
from ..models import PageLayout, PageSection

class PageLayoutSerializer(PageLayoutBaseSerializer):
    """Serializer configuration layout pour renderer"""
    
    page_title = serializers.CharField(source='page.title', read_only=True)
    page_url = serializers.CharField(source='page.url_path', read_only=True)
    
    class Meta:
        model = PageLayout
        fields = [
            'id', 'page', 'page_title', 'page_url',
            'render_strategy', 'layout_data', 'created_at', 'updated_at'
        ]
    
    def validate_layout_data(self, value):
        """Validation basique de la structure JSON"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Layout data doit être un objet JSON")
        return value

class PageSectionListSerializer(PageLayoutBaseSerializer):
    """Serializer liste sections - Données minimales"""
    
    page_title = serializers.CharField(source='page.title', read_only=True)
    section_type_display = serializers.CharField(source='get_section_type_display', read_only=True)
    parent_title = serializers.CharField(source='parent_section.data.title', read_only=True)
    has_children = serializers.SerializerMethodField()
    
    class Meta:
        model = PageSection
        fields = [
            'id', 'page', 'page_title', 'parent_section', 'parent_title',
            'section_type', 'section_type_display', 'order', 'is_active',
            'has_children', 'version'
        ]
    
    def get_has_children(self, obj):
        return obj.child_sections.exists()

class PageSectionDetailSerializer(PageLayoutBaseSerializer):
    """Serializer détail section avec enfants"""
    
    page_title = serializers.CharField(source='page.title', read_only=True)
    section_type_display = serializers.CharField(source='get_section_type_display', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = PageSection
        fields = [
            'id', 'page', 'page_title', 'parent_section',
            'section_type', 'section_type_display', 'data', 'layout_config',
            'order', 'is_active', 'version', 'created_by', 'created_by_username',
            'children', 'created_at', 'updated_at'
        ]
    
    def get_children(self, obj):
        children = obj.child_sections.filter(is_active=True).order_by('order')
        return PageSectionListSerializer(children, many=True).data

class PageSectionCreateSerializer(PageLayoutBaseSerializer):
    """Serializer création section avec validation"""
    
    # 🎯 AJOUTER L'ID dans les champs pour le retour après création
    id = serializers.IntegerField(read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = PageSection
        fields = [
            'id', 'page', 'parent_section', 'section_type', 'data',
            'layout_config', 'order', 'is_active', 'version',
            'created_by', 'created_by_username', 'created_at'  # 🎯 Champs utiles en retour
        ]
    
    def validate_data(self, value):
        """Validation structure JSON des données"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Data doit être un objet JSON")
        return value
    
    def validate_layout_config(self, value):
        """Validation configuration CSS Grid"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Layout config doit être un objet JSON")
        
        # Validation spécifique selon type de layout
        if 'columns' in value:
            columns = value['columns']
            if not isinstance(columns, list) or not all(isinstance(x, int) for x in columns):
                raise serializers.ValidationError("Columns doit être une liste d'entiers")
            
            if sum(columns) > 12:
                raise serializers.ValidationError("La somme des colonnes ne peut dépasser 12")
        
        return value
    
    def validate(self, data):
        """Validation business rules"""
        section_type = data.get('section_type')
        parent_section = data.get('parent_section')
        
        # Les layout containers ne peuvent pas avoir de parent
        if section_type and section_type.startswith('layout_') and parent_section:
            raise serializers.ValidationError({
                'parent_section': 'Les containers layout doivent être des sections racines'
            })
        
        # Les sections content doivent avoir un parent ou être racines
        if section_type and not section_type.startswith('layout_'):
            if parent_section and parent_section.parent_section:
                raise serializers.ValidationError({
                    'parent_section': 'Hiérarchie limitée à 2 niveaux maximum'
                })
        
        return data

class PageRenderDataSerializer(serializers.Serializer):
    """Serializer pour données de rendu Next.js"""
    
    strategy = serializers.CharField()
    sections = serializers.SerializerMethodField()
    
    def get_sections(self, obj):
        """Retourne hiérarchie sections pour rendu"""
        page = obj
        
        # Récupérer sections racines uniquement
        root_sections = page.sections.filter(
            parent_section__isnull=True,
            is_active=True
        ).order_by('order')
        
        # Sérialiser avec enfants
        return PageSectionDetailSerializer(root_sections, many=True).data