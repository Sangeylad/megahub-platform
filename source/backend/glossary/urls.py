# backend/glossary/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from glossary.views import TermCategoryViewSet, TermViewSet

# Router DRF pour les endpoints RESTful
router = DefaultRouter()
router.register(r'categories', TermCategoryViewSet, basename='termcategory')
router.register(r'terms', TermViewSet, basename='term')

app_name = 'glossary'

urlpatterns = [
    path('', include(router.urls)),
]