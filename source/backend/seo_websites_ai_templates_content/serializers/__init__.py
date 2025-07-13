# backend/seo_websites_ai_templates_content/serializers/__init__.py

from .seo_template_serializers import (
    SEOWebsiteTemplateListSerializer,
    SEOWebsiteTemplateDetailSerializer,
    SEOWebsiteTemplateWriteSerializer,
    SEOTemplateConfigSerializer,
    KeywordIntegrationRuleSerializer,
    PageTypeTemplateSerializer
)

__all__ = [
    'SEOWebsiteTemplateListSerializer',
    'SEOWebsiteTemplateDetailSerializer',
    'SEOWebsiteTemplateWriteSerializer',
    'SEOTemplateConfigSerializer',
    'KeywordIntegrationRuleSerializer',
    'PageTypeTemplateSerializer'
]
