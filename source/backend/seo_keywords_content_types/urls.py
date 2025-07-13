# backend/seo_keywords_content_types/urls.py

from rest_framework import routers
from .views import ContentTypeViewSet, KeywordContentTypeViewSet

router = routers.DefaultRouter()
router.register(r'types', ContentTypeViewSet, basename='content-types')
router.register(r'associations', KeywordContentTypeViewSet, basename='keyword-content-types')

urlpatterns = router.urls