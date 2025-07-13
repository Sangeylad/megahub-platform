# backend/seo_keywords_ppa/urls.py

from rest_framework import routers
from .views import PPAViewSet, KeywordPPAViewSet

router = routers.DefaultRouter()
router.register(r'questions', PPAViewSet, basename='ppa')
router.register(r'associations', KeywordPPAViewSet, basename='keyword-ppa')

urlpatterns = router.urls