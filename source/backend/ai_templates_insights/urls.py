# backend/ai_templates_insights/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TemplateRecommendationViewSet, TemplateInsightViewSet,
    OptimizationSuggestionViewSet, TrendAnalysisViewSet
)

router = DefaultRouter()
router.register(r'recommendations', TemplateRecommendationViewSet, basename='templaterecommendation')
router.register(r'insights', TemplateInsightViewSet, basename='templateinsight')
router.register(r'optimizations', OptimizationSuggestionViewSet, basename='optimizationsuggestion')
router.register(r'trends', TrendAnalysisViewSet, basename='trendanalysis')

urlpatterns = [
    path('', include(router.urls)),
]
