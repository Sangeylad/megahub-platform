# /var/www/megahub/backend/mailing_templates_core/serializers/template_serializers.py

from rest_framework import serializers
from common.serializers.mixins import DynamicFieldsSerializer
from common.serializers.mixins import StatsMixin
from ..models import EmailTemplate

class EmailTemplateListSerializer(DynamicFieldsSerializer):
    """Liste templates - champs essentiels"""
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = EmailTemplate
        fields = [
            'id', 'name', 'category', 'status', 'usage_count',
            'brand_name', 'created_by_name', 'is_favorite', 'created_at'
        ]

class EmailTemplateDetailSerializer(StatsMixin, DynamicFieldsSerializer):
    """Détail complet template"""
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    preview_url = serializers.SerializerMethodField()
    
    class Meta:
        model = EmailTemplate
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'usage_count', 'last_used_at']
        stats_fields = {
            'campaigns_using': 'get_campaigns_count',
            'avg_performance': 'get_avg_performance'
        }
    
    def get_preview_url(self, obj):
        """URL de prévisualisation du template"""
        if obj.preview_image:
            return obj.preview_image.url
        return None

class EmailTemplateWriteSerializer(DynamicFieldsSerializer):
    """Serializer pour création/modification templates"""
    
    class Meta:
        model = EmailTemplate
        fields = [
            'name', 'description', 'category', 'html_content', 
            'text_content', 'design_config', 'variables', 'tags'
        ]
    
    def validate_name(self, value):
        """Validation nom unique par brand"""
        request = self.context.get('request')
        if not request:
            return value
            
        if self.instance:
            qs = EmailTemplate.objects.filter(
                name=value,
                brand=request.current_brand
            ).exclude(pk=self.instance.pk)
        else:
            qs = EmailTemplate.objects.filter(
                name=value,
                brand=request.current_brand
            )
        
        if qs.exists():
            raise serializers.ValidationError(
                "Un template avec ce nom existe déjà pour cette marque."
            )
        return value
    
    def validate_html_content(self, value):
        """Validation HTML de base"""
        if not value or len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Le contenu HTML doit contenir au moins 10 caractères."
            )
        return value
