# backend/ai_templates_insights/admin/__init__.py
from .insights_admin import (
    TemplateRecommendationAdmin, TemplateInsightAdmin,
    OptimizationSuggestionAdmin, TrendAnalysisAdmin
)
__all__ = [
    'TemplateRecommendationAdmin', 'TemplateInsightAdmin',
    'OptimizationSuggestionAdmin', 'TrendAnalysisAdmin'
]
