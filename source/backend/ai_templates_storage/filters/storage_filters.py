# backend/ai_templates_storage/filters/storage_filters.py

import django_filters
from ..models import TemplateVersion

class TemplateVersionFilter(django_filters.FilterSet):
    """Filtres pour versions de templates"""
    template = django_filters.NumberFilter(field_name='template__id')
    template_name = django_filters.CharFilter(field_name='template__name', lookup_expr='icontains')
    is_current = django_filters.BooleanFilter()
    created_by = django_filters.NumberFilter(field_name='created_by__id')
    
    class Meta:
        model = TemplateVersion
        fields = ['template', 'template_name', 'is_current', 'created_by']
