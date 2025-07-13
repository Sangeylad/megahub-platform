# backend/seo_websites_ai_templates_content/serializers/seo_template_serializers.py

from rest_framework import serializers
from common.serializers.mixins import DynamicFieldsSerializer
from common.serializers.mixins import StatsMixin
from ..models import SEOWebsiteTemplate, SEOTemplateConfig, KeywordIntegrationRule, PageTypeTemplate

class SEOWebsiteTemplateListSerializer(DynamicFieldsSerializer):
    """Liste templates SEO - champs essentiels"""
    template_name = serializers.CharField(source='base_template.name', read_only=True)
    template_type = serializers.CharField(source='base_template.template_type.display_name', read_only=True)
    category_name = serializers.CharField(source='category.display_name', read_only=True)
    brand_name = serializers.CharField(source='base_template.brand.name', read_only=True)
    
    class Meta:
        model = SEOWebsiteTemplate
        fields = [
            'id', 'template_name', 'template_type', 'category_name', 'brand_name',
            'page_type', 'search_intent', 'target_word_count', 'created_at'
        ]

class SEOWebsiteTemplateDetailSerializer(StatsMixin, DynamicFieldsSerializer):
    """Détail template SEO - complet"""
    template_name = serializers.CharField(source='base_template.name', read_only=True)
    template_content = serializers.CharField(source='base_template.prompt_content', read_only=True)
    template_type = serializers.CharField(source='base_template.template_type.display_name', read_only=True)
    category_name = serializers.CharField(source='category.display_name', read_only=True)
    brand_name = serializers.CharField(source='base_template.brand.name', read_only=True)
    
    class Meta:
        model = SEOWebsiteTemplate
        fields = [
            'id', 'base_template', 'template_name', 'template_content', 'template_type',
            'category', 'category_name', 'brand_name', 'page_type', 'search_intent',
            'target_word_count', 'keyword_density_target', 'created_at', 'updated_at'
        ]
        read_only_fields = ['base_template']
        stats_fields = {
            'keyword_rules_count': 'get_keyword_rules_count',
            'has_advanced_config': 'get_has_advanced_config'
        }

class SEOWebsiteTemplateWriteSerializer(DynamicFieldsSerializer):
    """Création/modification templates SEO"""
    
    class Meta:
        model = SEOWebsiteTemplate
        fields = [
            'base_template', 'category', 'page_type', 'search_intent',
            'target_word_count', 'keyword_density_target'
        ]

class SEOTemplateConfigSerializer(DynamicFieldsSerializer):
    """Configuration SEO avancée"""
    template_name = serializers.CharField(source='seo_template.base_template.name', read_only=True)
    
    class Meta:
        model = SEOTemplateConfig
        fields = [
            'id', 'seo_template', 'template_name', 'h1_structure', 'h2_pattern',
            'meta_title_template', 'meta_description_template', 'internal_linking_rules',
            'schema_markup_type', 'created_at', 'updated_at'
        ]

class KeywordIntegrationRuleSerializer(DynamicFieldsSerializer):
    """Règles d'intégration mots-clés"""
    template_name = serializers.CharField(source='seo_template.base_template.name', read_only=True)
    
    class Meta:
        model = KeywordIntegrationRule
        fields = [
            'id', 'seo_template', 'template_name', 'keyword_type', 'placement_rules',
            'density_min', 'density_max', 'natural_variations', 'created_at'
        ]

class PageTypeTemplateSerializer(DynamicFieldsSerializer):
    """Templates prédéfinis par type de page"""
    
    class Meta:
        model = PageTypeTemplate
        fields = [
            'id', 'name', 'page_type', 'template_structure', 'default_sections',
            'required_variables', 'is_active', 'created_at', 'updated_at'
        ]
