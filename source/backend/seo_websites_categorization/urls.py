# backend/seo_websites_categorization/urls.py

from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import WebsiteCategoryViewSet, WebsiteCategorizationViewSet

# Router principal
router = DefaultRouter()
router.register(r'categories', WebsiteCategoryViewSet, basename='website-categories')
router.register(r'categorizations', WebsiteCategorizationViewSet, basename='website-categorizations')

urlpatterns = [
    path('', include(router.urls)),
]

# Endpoints générés automatiquement :
# GET/POST /categories/
# GET/PUT/DELETE /categories/{id}/
# GET /categories/tree/
# GET /categories/stats/
# POST /categories/reorder/
# GET/POST /categorizations/
# GET/PUT/DELETE /categorizations/{id}/
# POST /categorizations/bulk-create/
# POST /categorizations/bulk-delete/
# GET /categorizations/by-website/
# GET /categorizations/by-category/
# POST /categorizations/set-primary/