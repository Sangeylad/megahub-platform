# backend/brands_core/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from brands_core.views.brand_views import BrandViewSet

router = DefaultRouter()
# ✅ CORRECTION : Pas de préfixe 'brands' car l'URL parent est déjà /brands/
router.register(r'', BrandViewSet, basename='brand')

urlpatterns = [
    path('', include(router.urls)),
]