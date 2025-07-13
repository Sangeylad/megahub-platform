# backend/seo_websites_core/urls.py

from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import WebsiteViewSet

# Router principal
router = DefaultRouter()
router.register(r'', WebsiteViewSet, basename='websites')

urlpatterns = [
    path('', include(router.urls)),
]

# Endpoints générés automatiquement :
# GET/POST /websites/
# GET/PUT/DELETE /websites/{id}/
# GET /websites/{id}/stats/