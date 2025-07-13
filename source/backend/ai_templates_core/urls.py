# backend/ai_templates_core/urls.py
"""
URLs pour ai_templates_core
Router DRF avec endpoints intelligents
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TemplateTypeViewSet, BrandTemplateConfigViewSet, BaseTemplateViewSet

# ===== ROUTER DRF =====

router = DefaultRouter()

# Routes template types (lecture seule)
router.register(r'types', TemplateTypeViewSet, basename='templatetype')

# Routes config brands
router.register(r'brand-configs', BrandTemplateConfigViewSet, basename='brandtemplateconfig')

# Routes templates principales avec actions custom - RACINE VIDE car déjà préfixé
router.register(r'', BaseTemplateViewSet, basename='basetemplate')

# ===== URL PATTERNS =====

app_name = 'ai_templates_core'

urlpatterns = [
    # API endpoints via router
    path('', include(router.urls)),
]