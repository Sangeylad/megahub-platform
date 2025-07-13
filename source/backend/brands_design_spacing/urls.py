# backend/brands_design_spacing/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import BrandSpacingSystemViewSet, WebsiteLayoutConfigViewSet

router = DefaultRouter()
router.register(r'brand-spacing', BrandSpacingSystemViewSet, basename='brandspacingsystem')
router.register(r'website-configs', WebsiteLayoutConfigViewSet, basename='websitelayoutconfig')

urlpatterns = [
    path('', include(router.urls)),
]
