# backend/seo_pages_workflow/urls.py

from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import PageStatusViewSet, PageWorkflowHistoryViewSet, PageSchedulingViewSet

# Router principal
router = DefaultRouter()
router.register(r'status', PageStatusViewSet, basename='page-status')
router.register(r'history', PageWorkflowHistoryViewSet, basename='workflow-history')
router.register(r'scheduling', PageSchedulingViewSet, basename='page-scheduling')

urlpatterns = [
    path('', include(router.urls)),
]

# Endpoints générés automatiquement :
# GET/PUT /status/
# GET /status/{id}/
# GET /status/dashboard/
# POST /status/bulk-update/
# GET /history/
# GET /history/{id}/
# GET/POST /scheduling/
# PUT /scheduling/{id}/
# POST /scheduling/publish-ready/
