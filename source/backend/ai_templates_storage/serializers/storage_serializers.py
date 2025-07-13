# backend/ai_templates_storage/serializers/storage_serializers.py

from rest_framework import serializers
from common.serializers.mixins import DynamicFieldsSerializer
from ..models import TemplateVariable, TemplateVersion

class TemplateVariableSerializer(DynamicFieldsSerializer):
    """Serializer pour variables de templates"""
    
    class Meta:
        model = TemplateVariable
        fields = [
            'id', 'name', 'display_name', 'description', 'variable_type',
            'default_value', 'is_required', 'created_at'
        ]

class TemplateVersionListSerializer(DynamicFieldsSerializer):
    """Liste versions - champs essentiels"""
    template_name = serializers.CharField(source='template.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = TemplateVersion
        fields = [
            'id', 'template', 'template_name', 'version_number', 'is_current',
            'created_by_username', 'created_at', 'changelog'
        ]

class TemplateVersionDetailSerializer(DynamicFieldsSerializer):
    """Détail version - complet"""
    template_name = serializers.CharField(source='template.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = TemplateVersion
        fields = [
            'id', 'template', 'template_name', 'version_number', 'prompt_content',
            'changelog', 'is_current', 'created_by', 'created_by_username',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['template', 'version_number', 'created_by']

class TemplateVersionWriteSerializer(DynamicFieldsSerializer):
    """Création nouvelle version"""
    
    class Meta:
        model = TemplateVersion
        fields = ['template', 'prompt_content', 'changelog']
    
    def create(self, validated_data):
        """Ajoute created_by et gère is_current"""
        request = self.context['request']
        validated_data['created_by'] = request.user
        
        # Nouvelle version devient current
        template = validated_data['template']
        TemplateVersion.objects.filter(template=template).update(is_current=False)
        validated_data['is_current'] = True
        
        return super().create(validated_data)
