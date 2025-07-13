# backend/ai_templates_categories/filters/category_filters.py
import django_filters
from ..models import TemplateCategory, TemplateTag

class TemplateCategoryFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    parent = django_filters.NumberFilter()
    level = django_filters.NumberFilter()
    is_active = django_filters.BooleanFilter()
    
    class Meta:
        model = TemplateCategory
        fields = ['name', 'parent', 'level', 'is_active']

class TemplateTagFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    color = django_filters.CharFilter()
    is_active = django_filters.BooleanFilter()
    
    class Meta:
        model = TemplateTag
        fields = ['name', 'color', 'is_active']
