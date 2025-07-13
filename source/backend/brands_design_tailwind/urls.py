# backend/brands_design_tailwind/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import WebsiteTailwindConfigViewSet, TailwindThemeExportViewSet

router = DefaultRouter()
router.register(r'website-configs', WebsiteTailwindConfigViewSet, basename='websitetailwindconfig')
router.register(r'exports', TailwindThemeExportViewSet, basename='tailwindthemeexport')

urlpatterns = [
    path('', include(router.urls)),
]
