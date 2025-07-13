# backend/ai_templates_insights/admin/insights_admin.py
from django.contrib import admin
from ..models import TemplateRecommendation, TemplateInsight, OptimizationSuggestion, TrendAnalysis

@admin.register(TemplateRecommendation)
class TemplateRecommendationAdmin(admin.ModelAdmin):
    list_display = ['brand', 'user', 'recommended_template', 'recommendation_type', 'confidence_score']
    list_filter = ['recommendation_type', 'is_active', 'clicked']

@admin.register(TemplateInsight)
class TemplateInsightAdmin(admin.ModelAdmin):
    list_display = ['template', 'insight_type', 'severity', 'is_resolved', 'created_at']
    list_filter = ['insight_type', 'severity', 'is_resolved']

@admin.register(OptimizationSuggestion)
class OptimizationSuggestionAdmin(admin.ModelAdmin):
    list_display = ['template', 'suggestion_type', 'estimated_impact', 'is_implemented']
    list_filter = ['suggestion_type', 'estimated_impact', 'is_implemented']

@admin.register(TrendAnalysis)
class TrendAnalysisAdmin(admin.ModelAdmin):
    list_display = ['analysis_type', 'scope', 'trend_direction', 'trend_strength', 'created_at']
    list_filter = ['analysis_type', 'scope', 'trend_direction']
