# backend/seo_websites_ai_templates_content/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SEOWebsiteTemplateViewSet, SEOTemplateConfigViewSet,
    KeywordIntegrationRuleViewSet, PageTypeTemplateViewSet
)

router = DefaultRouter()
router.register(r'seo-templates', SEOWebsiteTemplateViewSet, basename='seowebsitetemplate')
router.register(r'seo-configs', SEOTemplateConfigViewSet, basename='seotemplateconfig')
router.register(r'keyword-rules', KeywordIntegrationRuleViewSet, basename='keywordintegrationrule')
router.register(r'page-type-templates', PageTypeTemplateViewSet, basename='pagetypetemplate')

urlpatterns = [
    path('', include(router.urls)),
]
