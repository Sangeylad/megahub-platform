# backend/task_monitoring/urls.py

from rest_framework.routers import DefaultRouter
from .views import TaskMetricsViewSet, AlertRuleViewSet, WorkerHealthViewSet

router = DefaultRouter()
router.register(r'metrics', TaskMetricsViewSet, basename='metrics')
router.register(r'alerts', AlertRuleViewSet, basename='alerts')
router.register(r'workers', WorkerHealthViewSet, basename='workers')

urlpatterns = router.urls
