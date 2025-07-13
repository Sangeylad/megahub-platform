# backend/ai_templates_analytics/serializers/analytics_serializers.py

from rest_framework import serializers
from common.serializers.mixins import DynamicFieldsSerializer
from ..models import TemplateUsageMetrics, TemplatePerformance, TemplatePopularity, TemplateFeedback

class TemplateUsageMetricsSerializer(DynamicFieldsSerializer):
    """Serializer pour métriques d'usage"""
    template_name = serializers.CharField(source='template.name', read_only=True)
    success_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = TemplateUsageMetrics
        fields = [
            'id', 'template', 'template_name', 'total_uses', 'successful_generations',
            'failed_generations', 'unique_users', 'last_used_at', 'avg_generation_time',
            'popularity_score', 'success_rate', 'created_at', 'updated_at'
        ]
        read_only_fields = ['template']

class TemplatePerformanceSerializer(DynamicFieldsSerializer):
    """Serializer pour performance détaillée"""
    template_name = serializers.CharField(source='template.name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = TemplatePerformance
        fields = [
            'id', 'template', 'template_name', 'user', 'user_username',
            'generation_time', 'tokens_used', 'output_quality_score',
            'variables_used', 'was_successful', 'error_message', 'created_at'
        ]
        read_only_fields = ['user']

class TemplatePopularitySerializer(DynamicFieldsSerializer):
    """Serializer pour classements popularité"""
    template_name = serializers.CharField(source='template.name', read_only=True)
    category_name = serializers.CharField(source='category.display_name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    
    class Meta:
        model = TemplatePopularity
        fields = [
            'id', 'template', 'template_name', 'category', 'category_name',
            'brand', 'brand_name', 'ranking_period', 'rank_position',
            'usage_count', 'period_start', 'period_end', 'created_at'
        ]

class TemplateFeedbackSerializer(DynamicFieldsSerializer):
    """Serializer pour feedback utilisateurs"""
    template_name = serializers.CharField(source='template.name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = TemplateFeedback
        fields = [
            'id', 'template', 'template_name', 'user', 'user_username',
            'rating', 'comment', 'feedback_type', 'is_public',
            'admin_response', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user']
