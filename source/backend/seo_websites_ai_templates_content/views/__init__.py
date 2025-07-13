# backend/seo_websites_ai_templates_content/views/__init__.py

from .seo_template_views import (
    SEOWebsiteTemplateViewSet, SEOTemplateConfigViewSet,
    KeywordIntegrationRuleViewSet, PageTypeTemplateViewSet
)

__all__ = [
    'SEOWebsiteTemplateViewSet', 'SEOTemplateConfigViewSet',
    'KeywordIntegrationRuleViewSet', 'PageTypeTemplateViewSet'
]
