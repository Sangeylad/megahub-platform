# backend/ai_templates_core/views/__init__.py
"""
Views pour ai_templates_core
Imports centralisés avec gestion conditionnelle des modules cross-app
"""

# Import des views principales (toujours disponibles)
from .template_views import (
    TemplateTypeViewSet,
    BrandTemplateConfigViewSet,
    BaseTemplateViewSet
)

# Import conditionnel des views cross-app si disponibles
try:
    from ai_templates_analytics.views import TemplateAnalyticsViewSet
    HAS_ANALYTICS_VIEWS = True
except ImportError:
    HAS_ANALYTICS_VIEWS = False

try:
    from ai_templates_workflow.views import TemplateWorkflowViewSet
    HAS_WORKFLOW_VIEWS = True
except ImportError:
    HAS_WORKFLOW_VIEWS = False

try:
    from ai_templates_insights.views import TemplateInsightsViewSet
    HAS_INSIGHTS_VIEWS = True
except ImportError:
    HAS_INSIGHTS_VIEWS = False

try:
    from ai_templates_storage.views import TemplateStorageViewSet
    HAS_STORAGE_VIEWS = True
except ImportError:
    HAS_STORAGE_VIEWS = False

# Export principal - ViewSets toujours disponibles
__all__ = [
    'TemplateTypeViewSet',
    'BrandTemplateConfigViewSet', 
    'BaseTemplateViewSet'
]

# Ajout conditionnel selon modules disponibles
if HAS_ANALYTICS_VIEWS:
    __all__.append('TemplateAnalyticsViewSet')

if HAS_WORKFLOW_VIEWS:
    __all__.append('TemplateWorkflowViewSet')

if HAS_INSIGHTS_VIEWS:
    __all__.append('TemplateInsightsViewSet')

if HAS_STORAGE_VIEWS:
    __all__.append('TemplateStorageViewSet')

# Configuration dynamique pour debugging
AVAILABLE_VIEWSETS = {
    'core': ['TemplateTypeViewSet', 'BrandTemplateConfigViewSet', 'BaseTemplateViewSet'],
    'analytics': ['TemplateAnalyticsViewSet'] if HAS_ANALYTICS_VIEWS else [],
    'workflow': ['TemplateWorkflowViewSet'] if HAS_WORKFLOW_VIEWS else [],
    'insights': ['TemplateInsightsViewSet'] if HAS_INSIGHTS_VIEWS else [],
    'storage': ['TemplateStorageViewSet'] if HAS_STORAGE_VIEWS else []
}

# Métadonnées pour debugging/monitoring
MODULES_STATUS = {
    'core': True,
    'analytics': HAS_ANALYTICS_VIEWS,
    'workflow': HAS_WORKFLOW_VIEWS,
    'insights': HAS_INSIGHTS_VIEWS,
    'storage': HAS_STORAGE_VIEWS
}