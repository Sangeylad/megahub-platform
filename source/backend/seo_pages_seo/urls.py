# backend/seo_pages_seo/urls.py

from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import PageSEOViewSet, PagePerformanceViewSet

# Router principal
router = DefaultRouter()
router.register(r'seo', PageSEOViewSet, basename='page-seo')
router.register(r'performance', PagePerformanceViewSet, basename='page-performance')

urlpatterns = [
    path('', include(router.urls)),
]

# Endpoints générés automatiquement :
# GET/POST /seo/
# GET/PUT /seo/{id}/
# POST /seo/bulk-update/
# GET /seo/sitemap-data/
# GET /performance/
# GET /performance/{id}/
# POST /performance/regenerate/
