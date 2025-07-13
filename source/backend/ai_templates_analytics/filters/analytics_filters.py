# backend/ai_templates_analytics/filters/analytics_filters.py
import django_filters
from ..models import TemplatePerformance, TemplateFeedback

class TemplatePerformanceFilter(django_filters.FilterSet):
    template = django_filters.NumberFilter()
    was_successful = django_filters.BooleanFilter()
    generation_time = django_filters.RangeFilter()
    
    class Meta:
        model = TemplatePerformance
        fields = ['template', 'was_successful', 'generation_time']

class TemplateFeedbackFilter(django_filters.FilterSet):
    template = django_filters.NumberFilter()
    rating = django_filters.NumberFilter()
    feedback_type = django_filters.CharFilter()
    is_public = django_filters.BooleanFilter()
    
    class Meta:
        model = TemplateFeedback
        fields = ['template', 'rating', 'feedback_type', 'is_public']
