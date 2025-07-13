# backend/ai_templates_insights/views/__init__.py

from .insights_views import (
    TemplateRecommendationViewSet, TemplateInsightViewSet,
    OptimizationSuggestionViewSet, TrendAnalysisViewSet
)

__all__ = [
    'TemplateRecommendationViewSet', 'TemplateInsightViewSet',
    'OptimizationSuggestionViewSet', 'TrendAnalysisViewSet'
]
