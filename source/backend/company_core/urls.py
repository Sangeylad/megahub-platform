# backend/company_core/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from company_core.views.company_views import CompanyViewSet

router = DefaultRouter()
router.register(r'', CompanyViewSet, basename='company')

urlpatterns = [
    path('', include(router.urls)),
]