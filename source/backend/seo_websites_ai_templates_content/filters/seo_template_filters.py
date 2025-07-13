# backend/seo_websites_ai_templates_content/filters/seo_template_filters.py
import django_filters
from ..models import SEOWebsiteTemplate, KeywordIntegrationRule

class SEOWebsiteTemplateFilter(django_filters.FilterSet):
    page_type = django_filters.CharFilter()
    search_intent = django_filters.CharFilter()
    category = django_filters.NumberFilter()
    target_word_count = django_filters.RangeFilter()
    
    class Meta:
        model = SEOWebsiteTemplate
        fields = ['page_type', 'search_intent', 'category', 'target_word_count']

class KeywordIntegrationRuleFilter(django_filters.FilterSet):
    keyword_type = django_filters.CharFilter()
    seo_template = django_filters.NumberFilter()
    
    class Meta:
        model = KeywordIntegrationRule
        fields = ['keyword_type', 'seo_template']
