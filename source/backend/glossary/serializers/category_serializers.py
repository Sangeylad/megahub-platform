# backend/glossary/serializers/category_serializers.py
from rest_framework import serializers
from glossary.models import TermCategory


class TermCategoryListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des catégories"""
    
    terms_count = serializers.ReadOnlyField()
    level = serializers.SerializerMethodField()
    url_path = serializers.SerializerMethodField()
    
    class Meta:
        model = TermCategory
        fields = [
            'id', 'name', 'slug', 'description', 'color', 'icon',
            'terms_count', 'level', 'url_path', 'is_active'
        ]
    
    def get_level(self, obj):
        return obj.get_level()
    
    def get_url_path(self, obj):
        return obj.get_url_path()


class TermCategorySerializer(serializers.ModelSerializer):
    """Serializer complet pour les catégories"""
    
    parent = TermCategoryListSerializer(read_only=True)
    children = TermCategoryListSerializer(many=True, read_only=True)
    terms_count = serializers.ReadOnlyField()
    level = serializers.SerializerMethodField()
    url_path = serializers.SerializerMethodField()
    full_path = serializers.SerializerMethodField()
    ancestors = serializers.SerializerMethodField()
    
    class Meta:
        model = TermCategory
        fields = [
            'id', 'name', 'slug', 'description', 'color', 'icon', 'order',
            'meta_title', 'meta_description', 'is_active',
            'parent', 'children', 'terms_count', 'level', 'url_path', 
            'full_path', 'ancestors', 'created_at', 'updated_at'
        ]
    
    def get_level(self, obj):
        return obj.get_level()
    
    def get_url_path(self, obj):
        return obj.get_url_path()
    
    def get_full_path(self, obj):
        return obj.get_full_path()
    
    def get_ancestors(self, obj):
        return TermCategoryListSerializer(obj.get_ancestors(), many=True).data


class TermCategoryTreeSerializer(serializers.ModelSerializer):
    """Serializer pour l'arbre hiérarchique des catégories"""
    
    children = serializers.SerializerMethodField()
    terms_count = serializers.ReadOnlyField()
    
    class Meta:
        model = TermCategory
        fields = [
            'id', 'name', 'slug', 'color', 'icon', 
            'terms_count', 'children'
        ]
    
    def get_children(self, obj):
        if obj.children.exists():
            return TermCategoryTreeSerializer(
                obj.children.filter(is_active=True).order_by('order', 'name'), 
                many=True
            ).data
        return []