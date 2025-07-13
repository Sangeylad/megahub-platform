# backend/ai_templates_analytics/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TemplateUsageMetricsViewSet, TemplatePerformanceViewSet,
    TemplatePopularityViewSet, TemplateFeedbackViewSet
)

router = DefaultRouter()
router.register(r'usage-metrics', TemplateUsageMetricsViewSet, basename='templateusagemetrics')
router.register(r'performance', TemplatePerformanceViewSet, basename='templateperformance')
router.register(r'popularity', TemplatePopularityViewSet, basename='templatepopularity')
router.register(r'feedback', TemplateFeedbackViewSet, basename='templatefeedback')

urlpatterns = [
    path('', include(router.urls)),
]
