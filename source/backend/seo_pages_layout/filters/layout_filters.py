# backend/seo_pages_layout/filters/layout_filters.py

import django_filters
from django.db import models

from ..models import PageLayout, PageSection

class PageLayoutFilter(django_filters.FilterSet):
    """Filtres pour configurations layout"""
    
    page = django_filters.NumberFilter()
    website = django_filters.NumberFilter(field_name='page__website')
    render_strategy = django_filters.ChoiceFilter(choices=PageLayout.RENDER_STRATEGY_CHOICES)
    
    # Filtres par contenu
    has_layout_data = django_filters.BooleanFilter(method='filter_has_layout_data')
    
    class Meta:
        model = PageLayout
        fields = ['page', 'render_strategy']
    
    def filter_has_layout_data(self, queryset, name, value):
        """Filtre layouts avec/sans données"""
        if value:
            return queryset.exclude(layout_data={})
        else:
            return queryset.filter(layout_data={})

class PageSectionFilter(django_filters.FilterSet):
    """Filtres pour sections du page builder"""
    
    page = django_filters.NumberFilter()
    website = django_filters.NumberFilter(field_name='page__website')
    parent_section = django_filters.NumberFilter()
    section_type = django_filters.ChoiceFilter(choices=PageSection.SECTION_TYPE_CHOICES)
    is_active = django_filters.BooleanFilter()
    created_by = django_filters.NumberFilter()
    version = django_filters.CharFilter()
    
    # Filtres hiérarchiques
    is_root = django_filters.BooleanFilter(method='filter_is_root')
    has_children = django_filters.BooleanFilter(method='filter_has_children')
    is_layout_container = django_filters.BooleanFilter(method='filter_is_layout_container')
    
    # Filtres par dates
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    # Recherche
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = PageSection
        fields = ['page', 'parent_section', 'section_type', 'is_active', 'created_by']
    
    def filter_is_root(self, queryset, name, value):
        """Filtre sections racines (sans parent)"""
        if value:
            return queryset.filter(parent_section__isnull=True)
        else:
            return queryset.filter(parent_section__isnull=False)
    
    def filter_has_children(self, queryset, name, value):
        """Filtre sections avec/sans enfants"""
        if value:
            return queryset.filter(child_sections__isnull=False).distinct()
        else:
            return queryset.filter(child_sections__isnull=True)
    
    def filter_is_layout_container(self, queryset, name, value):
        """Filtre containers layout vs sections content"""
        if value:
            return queryset.filter(section_type__startswith='layout_')
        else:
            return queryset.exclude(section_type__startswith='layout_')
    
    def filter_search(self, queryset, name, value):
        """Recherche dans données JSON des sections"""
        return queryset.filter(
            models.Q(data__title__icontains=value) |
            models.Q(page__title__icontains=value)
        )
