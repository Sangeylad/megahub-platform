# backend/blog_content/urls.py

from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import BlogArticleViewSet, BlogAuthorViewSet, BlogTagViewSet

router = DefaultRouter()
router.register(r'articles', BlogArticleViewSet, basename='articles')
router.register(r'authors', BlogAuthorViewSet, basename='authors')
router.register(r'tags', BlogTagViewSet, basename='tags')

urlpatterns = [
    path('', include(router.urls)),
]