# backend/ai_templates_categories/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TemplateCategoryViewSet, TemplateTagViewSet, CategoryPermissionViewSet

router = DefaultRouter()
# Plus de catch-all, routes explicites
router.register(r'list', TemplateCategoryViewSet, basename='templatecategory')  # /templates/categories/list/
router.register(r'tags', TemplateTagViewSet, basename='templatetag')           # /templates/categories/tags/
router.register(r'permissions', CategoryPermissionViewSet, basename='categorypermission') # /templates/categories/permissions/

urlpatterns = [
    path('', include(router.urls)),
]