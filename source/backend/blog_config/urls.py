# backend/blog_config/urls.py

from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import BlogConfigViewSet

router = DefaultRouter()
router.register(r'', BlogConfigViewSet, basename='config')

urlpatterns = [
    path('', include(router.urls)),
]