# backend/ai_usage/urls.py

from rest_framework import routers
from .views import AIJobUsageViewSet, AIUsageAlertViewSet

router = routers.DefaultRouter()
router.register(r'usage', AIJobUsageViewSet, basename='ai-usage')
router.register(r'alerts', AIUsageAlertViewSet, basename='ai-alerts')

urlpatterns = router.urls
