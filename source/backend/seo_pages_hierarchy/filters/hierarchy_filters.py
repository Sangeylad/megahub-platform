# backend/seo_pages_hierarchy/filters/hierarchy_filters.py

import django_filters
from django.db import models

from ..models import PageHierarchy, PageBreadcrumb

class PageHierarchyFilter(django_filters.FilterSet):
    """Filtres pour hiérarchie des pages"""
    
    page = django_filters.NumberFilter()
    parent = django_filters.NumberFilter()
    website = django_filters.NumberFilter(field_name='page__website')
    
    # Filtres par niveau
    level = django_filters.NumberFilter(method='filter_by_level')
    is_root = django_filters.BooleanFilter(method='filter_is_root')
    has_children = django_filters.BooleanFilter(method='filter_has_children')
    
    # Recherche dans titres de page
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = PageHierarchy
        fields = ['page', 'parent']
    
    def filter_by_level(self, queryset, name, value):
        """Filtre par niveau hiérarchique"""
        # Forcer un ordering simple pour éviter la boucle
        queryset = queryset.order_by('id')
        
        if value == 1:
            return queryset.filter(parent__isnull=True)
        elif value == 2:
            return queryset.filter(parent__isnull=False, parent__hierarchy__parent__isnull=True)
        elif value == 3:
            return queryset.filter(parent__isnull=False, parent__hierarchy__parent__isnull=False)
        return queryset
    
    def filter_is_root(self, queryset, name, value):
        """Filtre pages racines (sans parent)"""
        if value:
            return queryset.filter(parent__isnull=True)
        else:
            return queryset.filter(parent__isnull=False)
    
    def filter_has_children(self, queryset, name, value):
        """Filtre pages avec/sans enfants"""
        if value:
            return queryset.filter(page__children_hierarchy__isnull=False).distinct()
        else:
            return queryset.filter(page__children_hierarchy__isnull=True)
    
    def filter_search(self, queryset, name, value):
        """Recherche dans titre et URL des pages"""
        return queryset.filter(
            models.Q(page__title__icontains=value) |
            models.Q(page__url_path__icontains=value)
        )

class PageBreadcrumbFilter(django_filters.FilterSet):
    """Filtres pour breadcrumbs"""
    
    page = django_filters.NumberFilter()
    website = django_filters.NumberFilter(field_name='page__website')
    
    # Filtres par contenu breadcrumb
    has_breadcrumb = django_filters.BooleanFilter(method='filter_has_breadcrumb')
    breadcrumb_length = django_filters.NumberFilter(method='filter_breadcrumb_length')
    
    class Meta:
        model = PageBreadcrumb
        fields = ['page']
    
    def filter_has_breadcrumb(self, queryset, name, value):
        """Filtre breadcrumbs avec/sans contenu"""
        if value:
            return queryset.exclude(breadcrumb_json=[])
        else:
            return queryset.filter(breadcrumb_json=[])
    
    def filter_breadcrumb_length(self, queryset, name, value):
        """Filtre par longueur du breadcrumb"""
        return queryset.extra(
            where=["JSON_LENGTH(breadcrumb_json) = %s"],
            params=[value]
        )
