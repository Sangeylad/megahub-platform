# backend/company_features/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from company_features.views.features_views import FeatureViewSet, CompanyFeatureViewSet

router = DefaultRouter()
router.register(r'available', FeatureViewSet, basename='feature')
router.register(r'subscriptions', CompanyFeatureViewSet, basename='company-feature')

urlpatterns = [
    path('', include(router.urls)),
]