# backend/seo_keywords_cocoons/urls.py

from rest_framework import routers
from .views import SemanticCocoonViewSet, CocoonCategoryViewSet

router = routers.DefaultRouter()

# 🔥 ORDRE CRUCIAL : Spécifique d'abord, générique ensuite
router.register(r'categories', CocoonCategoryViewSet, basename='cocoon-categories')
router.register(r'', SemanticCocoonViewSet, basename='semantic-cocoons')

urlpatterns = router.urls