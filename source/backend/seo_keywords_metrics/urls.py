# backend/seo_keywords_metrics/urls.py

from rest_framework import routers
from .views import KeywordMetricsViewSet

router = routers.DefaultRouter()
router.register(r'metrics', KeywordMetricsViewSet, basename='keyword-metrics')

urlpatterns = router.urls