# backend/task_core/urls.py

from rest_framework.routers import DefaultRouter
from .views import BaseTaskViewSet

router = DefaultRouter()
router.register(r'', BaseTaskViewSet, basename='tasks')  # 🎯 Vide au lieu de 'tasks'

urlpatterns = router.urls