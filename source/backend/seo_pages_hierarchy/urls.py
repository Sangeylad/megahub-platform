# backend/seo_pages_hierarchy/urls.py

from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import PageHierarchyViewSet, PageBreadcrumbViewSet

# Router principal
router = DefaultRouter()
router.register(r'hierarchy', PageHierarchyViewSet, basename='page-hierarchy')
router.register(r'breadcrumbs', PageBreadcrumbViewSet, basename='page-breadcrumbs')

urlpatterns = [
    path('', include(router.urls)),
]

# Endpoints générés automatiquement :
# GET/POST /hierarchy/
# GET/PUT/DELETE /hierarchy/{id}/
# GET /hierarchy/tree/
# POST /hierarchy/rebuild/
# GET /breadcrumbs/
# GET /breadcrumbs/{id}/
# POST /breadcrumbs/{id}/regenerate/
