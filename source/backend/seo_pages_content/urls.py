# backend/seo_pages_content/urls.py

from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import PageViewSet

# Router principal
router = DefaultRouter()
router.register(r'', PageViewSet, basename='pages') 

urlpatterns = [
    path('', include(router.urls)),
]

# Endpoints générés automatiquement :
# GET/POST /pages/
# GET/PUT/DELETE /pages/{id}/
# GET /pages/by-website/
# POST /pages/bulk-create/