# backend/seo_keywords_base/urls.py

from rest_framework.routers import DefaultRouter
from .views import KeywordViewSet

router = DefaultRouter()
router.register(r'', KeywordViewSet, basename='keywords')  # ✅ Chaîne vide

urlpatterns = router.urls