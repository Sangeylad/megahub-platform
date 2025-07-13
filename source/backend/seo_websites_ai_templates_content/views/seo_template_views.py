# backend/seo_websites_ai_templates_content/views/seo_template_views.py

from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from common.views.mixins import BrandScopedViewSetMixin, AnalyticsViewSetMixin
from common.permissions.business_permissions import IsAuthenticated, IsBrandMember
from ..models import SEOWebsiteTemplate, SEOTemplateConfig, KeywordIntegrationRule, PageTypeTemplate
from ..serializers import (
    SEOWebsiteTemplateListSerializer, SEOWebsiteTemplateDetailSerializer, SEOWebsiteTemplateWriteSerializer,
    SEOTemplateConfigSerializer, KeywordIntegrationRuleSerializer, PageTypeTemplateSerializer
)
from ..filters import SEOWebsiteTemplateFilter, KeywordIntegrationRuleFilter

class SEOWebsiteTemplateViewSet(
    BrandScopedViewSetMixin,
    AnalyticsViewSetMixin,
    ModelViewSet
):
    """Templates SEO spécialisés"""
    queryset = SEOWebsiteTemplate.objects.select_related('base_template', 'category', 'base_template__brand')
    permission_classes = [IsAuthenticated, IsBrandMember]
    filterset_class = SEOWebsiteTemplateFilter
    ordering = ['-created_at']
    brand_field = 'base_template__brand'
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SEOWebsiteTemplateListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return SEOWebsiteTemplateWriteSerializer
        return SEOWebsiteTemplateDetailSerializer
    
    @action(detail=False, methods=['get'])
    def by_page_type(self, request):
        """Templates groupés par type de page"""
        queryset = self.filter_queryset(self.get_queryset())
        templates_by_type = {}
        
        for template in queryset:
            page_type = template.page_type
            if page_type not in templates_by_type:
                templates_by_type[page_type] = []
            templates_by_type[page_type].append(SEOWebsiteTemplateListSerializer(template).data)
        
        return Response(templates_by_type)
    
    @action(detail=False, methods=['get'])
    def by_intent(self, request):
        """Templates groupés par intention de recherche"""
        queryset = self.filter_queryset(self.get_queryset())
        templates_by_intent = {}
        
        for template in queryset:
            intent = template.search_intent
            if intent not in templates_by_intent:
                templates_by_intent[intent] = []
            templates_by_intent[intent].append(SEOWebsiteTemplateListSerializer(template).data)
        
        return Response(templates_by_intent)

class SEOTemplateConfigViewSet(BrandScopedViewSetMixin, ModelViewSet):
    """Configuration SEO avancée"""
    queryset = SEOTemplateConfig.objects.select_related('seo_template__base_template')
    serializer_class = SEOTemplateConfigSerializer
    permission_classes = [IsAuthenticated, IsBrandMember]
    brand_field = 'seo_template__base_template__brand'

class KeywordIntegrationRuleViewSet(BrandScopedViewSetMixin, ModelViewSet):
    """Règles d'intégration mots-clés"""
    queryset = KeywordIntegrationRule.objects.select_related('seo_template__base_template')
    serializer_class = KeywordIntegrationRuleSerializer
    permission_classes = [IsAuthenticated, IsBrandMember]
    filterset_class = KeywordIntegrationRuleFilter
    brand_field = 'seo_template__base_template__brand'

class PageTypeTemplateViewSet(ReadOnlyModelViewSet):
    """Templates prédéfinis par type de page"""
    queryset = PageTypeTemplate.objects.filter(is_active=True)
    serializer_class = PageTypeTemplateSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['page_type', 'name']
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Templates groupés par type de page"""
        templates_by_type = {}
        for template in self.get_queryset():
            page_type = template.page_type
            if page_type not in templates_by_type:
                templates_by_type[page_type] = []
            templates_by_type[page_type].append(PageTypeTemplateSerializer(template).data)
        
        return Response(templates_by_type)
