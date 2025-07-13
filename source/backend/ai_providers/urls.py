# backend/ai_providers/urls.py

from rest_framework import routers
from .views import AIProviderViewSet, AICredentialsViewSet

router = routers.DefaultRouter()
router.register(r'providers', AIProviderViewSet, basename='ai-providers')
router.register(r'credentials', AICredentialsViewSet, basename='ai-credentials')

urlpatterns = router.urls
