# backend/brands_design_typography/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import BrandTypographyViewSet, WebsiteTypographyConfigViewSet

router = DefaultRouter()
router.register(r'brand-typography', BrandTypographyViewSet, basename='brandtypography')
router.register(r'website-configs', WebsiteTypographyConfigViewSet, basename='websitetypographyconfig')

urlpatterns = [
    path('', include(router.urls)),
]
