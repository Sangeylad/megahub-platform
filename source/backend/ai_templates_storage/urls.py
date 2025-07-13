# backend/ai_templates_storage/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TemplateVariableViewSet, TemplateVersionViewSet

router = DefaultRouter()
router.register(r'variables', TemplateVariableViewSet, basename='templatevariable')
router.register(r'versions', TemplateVersionViewSet, basename='templateversion')

urlpatterns = [
    path('', include(router.urls)),
]
