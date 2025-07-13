# backend/blog_editor/urls.py

from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import BlogContentViewSet

router = DefaultRouter()
router.register(r'content', BlogContentViewSet, basename='content')

urlpatterns = [
    path('', include(router.urls)),
]