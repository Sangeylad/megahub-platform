# backend/ai_templates_categories/serializers/category_serializers.py

from rest_framework import serializers
from common.serializers.mixins import DynamicFieldsSerializer
from ..models import TemplateCategory, TemplateTag, CategoryPermission

class TemplateCategorySerializer(DynamicFieldsSerializer):
    """Serializer pour catégories de templates"""
    parent_name = serializers.CharField(source='parent.display_name', read_only=True)
    children_count = serializers.SerializerMethodField()
    full_path = serializers.SerializerMethodField()
    
    class Meta:
        model = TemplateCategory
        fields = [
            'id', 'name', 'display_name', 'description', 'parent', 'parent_name',
            'level', 'sort_order', 'is_active', 'icon_name', 'children_count',
            'full_path', 'created_at', 'updated_at'
        ]
    
    def get_children_count(self, obj):
        return obj.children.filter(is_active=True).count()
    
    def get_full_path(self, obj):
        """Chemin complet de la catégorie"""
        path = []
        current = obj
        while current:
            path.insert(0, current.display_name)
            current = current.parent
        return ' > '.join(path)

class TemplateTagSerializer(DynamicFieldsSerializer):
    """Serializer pour tags de templates"""
    
    class Meta:
        model = TemplateTag
        fields = [
            'id', 'name', 'display_name', 'description', 'color',
            'is_active', 'usage_count', 'created_at'
        ]
        read_only_fields = ['usage_count']

class CategoryPermissionSerializer(DynamicFieldsSerializer):
    """Serializer pour permissions de catégories"""
    category_name = serializers.CharField(source='category.display_name', read_only=True)
    
    class Meta:
        model = CategoryPermission
        fields = [
            'id', 'category', 'category_name', 'permission_type',
            'required_plan', 'is_active', 'created_at'
        ]
