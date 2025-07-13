# backend/ai_templates_insights/filters/insights_filters.py
import django_filters
from ..models import TemplateRecommendation, TemplateInsight

class TemplateRecommendationFilter(django_filters.FilterSet):
    recommendation_type = django_filters.CharFilter()
    is_active = django_filters.BooleanFilter()
    clicked = django_filters.BooleanFilter()
    
    class Meta:
        model = TemplateRecommendation
        fields = ['recommendation_type', 'is_active', 'clicked']

class TemplateInsightFilter(django_filters.FilterSet):
    insight_type = django_filters.CharFilter()
    severity = django_filters.CharFilter()
    is_resolved = django_filters.BooleanFilter()
    
    class Meta:
        model = TemplateInsight
        fields = ['insight_type', 'severity', 'is_resolved']
