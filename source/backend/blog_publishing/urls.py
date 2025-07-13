# backend/blog_publishing/urls.py

from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views.publishing_views import BlogPublishingStatusViewSet, BlogScheduledPublicationViewSet

router = DefaultRouter()
router.register(r'status', BlogPublishingStatusViewSet, basename='status')
router.register(r'scheduled', BlogScheduledPublicationViewSet, basename='scheduled')

urlpatterns = [
    path('', include(router.urls)),
]