# backend/ai_core/urls.py

from rest_framework import routers
from .views import AIJobViewSet, AIJobTypeViewSet

router = routers.DefaultRouter()
router.register(r'jobs', AIJobViewSet, basename='ai-jobs')
router.register(r'job-types', AIJobTypeViewSet, basename='ai-job-types')

urlpatterns = router.urls
