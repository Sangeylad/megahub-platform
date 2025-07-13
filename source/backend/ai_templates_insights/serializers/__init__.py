# backend/ai_templates_insights/serializers/__init__.py

from .insights_serializers import (
    TemplateRecommendationSerializer,
    TemplateInsightSerializer,
    OptimizationSuggestionSerializer,
    TrendAnalysisSerializer
)

__all__ = [
    'TemplateRecommendationSerializer',
    'TemplateInsightSerializer',
    'OptimizationSuggestionSerializer',
    'TrendAnalysisSerializer'
]
