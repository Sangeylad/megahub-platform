# backend/seo_pages_layout/urls.py

from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import PageLayoutViewSet, PageSectionViewSet

# Router principal
router = DefaultRouter()
router.register(r'layouts', PageLayoutViewSet, basename='page-layouts')
router.register(r'sections', PageSectionViewSet, basename='page-sections')

urlpatterns = [
    path('', include(router.urls)),
]

# Endpoints générés automatiquement :
# GET/POST /layouts/
# GET/PUT/DELETE /layouts/{id}/
# GET /layouts/render_data/
# GET/POST /sections/
# GET/PUT/DELETE /sections/{id}/
# POST /sections/reorder/
# POST /sections/{id}/duplicate/
