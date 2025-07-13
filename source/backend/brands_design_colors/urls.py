# backend/brands_design_colors/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import BrandColorPaletteViewSet, WebsiteColorConfigViewSet

router = DefaultRouter()
router.register(r'brand-palettes', BrandColorPaletteViewSet, basename='brandcolorpalette')
router.register(r'website-configs', WebsiteColorConfigViewSet, basename='websitecolorconfig')

urlpatterns = [
    path('', include(router.urls)),
]
