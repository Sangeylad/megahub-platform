# backend/seo_pages_keywords/urls.py

from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import PageKeywordViewSet

# Router principal
router = DefaultRouter()
router.register(r'page-keywords', PageKeywordViewSet, basename='page-keywords')

urlpatterns = [
    path('', include(router.urls)),
]

# Endpoints générés automatiquement :
# GET/POST /page-keywords/
# GET/PUT/DELETE /page-keywords/{id}/
# POST /page-keywords/bulk-create/
# GET /page-keywords/stats/
