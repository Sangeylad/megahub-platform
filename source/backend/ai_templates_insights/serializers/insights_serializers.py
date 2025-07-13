# backend/ai_templates_insights/serializers/insights_serializers.py

from rest_framework import serializers
from common.serializers.mixins import DynamicFieldsSerializer
from ..models import TemplateRecommendation, TemplateInsight, OptimizationSuggestion, TrendAnalysis

class TemplateRecommendationSerializer(DynamicFieldsSerializer):
    """Serializer pour recommandations"""
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    template_name = serializers.CharField(source='recommended_template.name', read_only=True)
    
    class Meta:
        model = TemplateRecommendation
        fields = [
            'id', 'brand', 'brand_name', 'user', 'user_username',
            'recommended_template', 'template_name', 'recommendation_type',
            'confidence_score', 'reasoning', 'priority', 'is_active',
            'clicked', 'clicked_at', 'created_at'
        ]
        read_only_fields = ['brand', 'user']

class TemplateInsightSerializer(DynamicFieldsSerializer):
    """Serializer pour insights automatiques"""
    template_name = serializers.CharField(source='template.name', read_only=True)
    
    class Meta:
        model = TemplateInsight
        fields = [
            'id', 'template', 'template_name', 'insight_type', 'title',
            'description', 'severity', 'data_source', 'is_resolved',
            'resolved_at', 'auto_generated', 'created_at'
        ]

class OptimizationSuggestionSerializer(DynamicFieldsSerializer):
    """Serializer pour suggestions d'optimisation"""
    template_name = serializers.CharField(source='template.name', read_only=True)
    
    class Meta:
        model = OptimizationSuggestion
        fields = [
            'id', 'template', 'template_name', 'suggestion_type', 'title',
            'description', 'implementation_difficulty', 'estimated_impact',
            'supporting_data', 'is_implemented', 'implemented_at', 'created_at'
        ]

class TrendAnalysisSerializer(DynamicFieldsSerializer):
    """Serializer pour analyses de tendances"""
    
    class Meta:
        model = TrendAnalysis
        fields = [
            'id', 'analysis_type', 'scope', 'scope_id', 'period_start',
            'period_end', 'trend_direction', 'trend_strength', 'key_findings',
            'visualization_data', 'created_at'
        ]
