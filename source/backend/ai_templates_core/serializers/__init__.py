# backend/ai_templates_core/serializers/__init__.py
"""
Serializers pour ai_templates_core
Imports centralisés avec gestion conditionnelle des modules cross-app
"""

# Import des serializers principaux (toujours disponibles)
from .template_serializers import (
    TemplateTypeSerializer,
    BrandTemplateConfigSerializer,
    BaseTemplateListSerializer,
    BaseTemplateDetailSerializer,
    BaseTemplateWriteSerializer
)

# Import conditionnel des serializers cross-app si disponibles
try:
    from ai_templates_analytics.serializers import (
        TemplateAnalyticsSerializer,
        TemplateStatsSerializer
    )
    HAS_ANALYTICS_SERIALIZERS = True
except ImportError:
    HAS_ANALYTICS_SERIALIZERS = False

try:
    from ai_templates_workflow.serializers import (
        TemplateApprovalSerializer,
        TemplateValidationSerializer
    )
    HAS_WORKFLOW_SERIALIZERS = True
except ImportError:
    HAS_WORKFLOW_SERIALIZERS = False

try:
    from ai_templates_insights.serializers import (
        TemplateInsightSerializer,
        TemplateRecommendationSerializer
    )
    HAS_INSIGHTS_SERIALIZERS = True
except ImportError:
    HAS_INSIGHTS_SERIALIZERS = False

try:
    from ai_templates_storage.serializers import (
        TemplateVersionSerializer,
        TemplateVariableSerializer
    )
    HAS_STORAGE_SERIALIZERS = True
except ImportError:
    HAS_STORAGE_SERIALIZERS = False

try:
    from ai_templates_categories.serializers import (
        TemplateCategorySerializer,
        TemplateTagSerializer
    )
    HAS_CATEGORIES_SERIALIZERS = True
except ImportError:
    HAS_CATEGORIES_SERIALIZERS = False

try:
    from seo_websites_ai_templates_content.serializers import (
        SEOWebsiteTemplateSerializer,
        SEOTemplateConfigSerializer
    )
    HAS_SEO_SERIALIZERS = True
except ImportError:
    HAS_SEO_SERIALIZERS = False

# Export principal - Serializers toujours disponibles
__all__ = [
    'TemplateTypeSerializer',
    'BrandTemplateConfigSerializer',
    'BaseTemplateListSerializer',
    'BaseTemplateDetailSerializer',
    'BaseTemplateWriteSerializer'
]

# Ajout conditionnel selon modules disponibles
if HAS_ANALYTICS_SERIALIZERS:
    __all__.extend(['TemplateAnalyticsSerializer', 'TemplateStatsSerializer'])

if HAS_WORKFLOW_SERIALIZERS:
    __all__.extend(['TemplateApprovalSerializer', 'TemplateValidationSerializer'])

if HAS_INSIGHTS_SERIALIZERS:
    __all__.extend(['TemplateInsightSerializer', 'TemplateRecommendationSerializer'])

if HAS_STORAGE_SERIALIZERS:
    __all__.extend(['TemplateVersionSerializer', 'TemplateVariableSerializer'])

if HAS_CATEGORIES_SERIALIZERS:
    __all__.extend(['TemplateCategorySerializer', 'TemplateTagSerializer'])

if HAS_SEO_SERIALIZERS:
    __all__.extend(['SEOWebsiteTemplateSerializer', 'SEOTemplateConfigSerializer'])

# Configuration dynamique pour debugging
AVAILABLE_SERIALIZERS = {
    'core': [
        'TemplateTypeSerializer', 'BrandTemplateConfigSerializer',
        'BaseTemplateListSerializer', 'BaseTemplateDetailSerializer',
        'BaseTemplateWriteSerializer'
    ],
    'analytics': ['TemplateAnalyticsSerializer', 'TemplateStatsSerializer'] if HAS_ANALYTICS_SERIALIZERS else [],
    'workflow': ['TemplateApprovalSerializer', 'TemplateValidationSerializer'] if HAS_WORKFLOW_SERIALIZERS else [],
    'insights': ['TemplateInsightSerializer', 'TemplateRecommendationSerializer'] if HAS_INSIGHTS_SERIALIZERS else [],
    'storage': ['TemplateVersionSerializer', 'TemplateVariableSerializer'] if HAS_STORAGE_SERIALIZERS else [],
    'categories': ['TemplateCategorySerializer', 'TemplateTagSerializer'] if HAS_CATEGORIES_SERIALIZERS else [],
    'seo': ['SEOWebsiteTemplateSerializer', 'SEOTemplateConfigSerializer'] if HAS_SEO_SERIALIZERS else []
}

# Métadonnées pour debugging/monitoring
MODULES_STATUS = {
    'core': True,
    'analytics': HAS_ANALYTICS_SERIALIZERS,
    'workflow': HAS_WORKFLOW_SERIALIZERS,
    'insights': HAS_INSIGHTS_SERIALIZERS,
    'storage': HAS_STORAGE_SERIALIZERS,
    'categories': HAS_CATEGORIES_SERIALIZERS,
    'seo': HAS_SEO_SERIALIZERS
}

# Helper pour obtenir serializer selon context
def get_template_serializer(action='list', include_cross_app=True):
    """
    Helper pour obtenir le bon serializer selon l'action
    
    Args:
        action: 'list', 'detail', 'write'
        include_cross_app: Inclure serializers cross-app si disponibles
    
    Returns:
        Classe serializer appropriée
    """
    if action == 'list':
        return BaseTemplateListSerializer
    elif action in ['create', 'update', 'partial_update', 'write']:
        return BaseTemplateWriteSerializer
    else:  # detail par défaut
        return BaseTemplateDetailSerializer

# Helper pour debug des modules
def get_modules_info():
    """Retourne info détaillée sur modules disponibles"""
    return {
        'status': MODULES_STATUS,
        'available_serializers': AVAILABLE_SERIALIZERS,
        'total_serializers': len(__all__)
    }