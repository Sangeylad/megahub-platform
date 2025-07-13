# backend/blog_collections/urls.py

from rest_framework import routers
from .views import BlogCollectionViewSet, BlogCollectionItemViewSet

router = routers.DefaultRouter()
router.register(r'', BlogCollectionViewSet, basename='collections')  # 🎯 Route racine
router.register(r'items', BlogCollectionItemViewSet, basename='collection-items')  # Plus court

urlpatterns = router.urls