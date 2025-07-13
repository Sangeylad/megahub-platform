# backend/seo_websites_categorization/filters/category_filters.py

import django_filters
from django.db import models

from ..models import WebsiteCategory, WebsiteCategorization

class WebsiteCategoryFilter(django_filters.FilterSet):
    """Filtres pour les catégories de websites"""
    
    # Filtres textuels
    name = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    slug = django_filters.CharFilter(lookup_expr='icontains')
    
    # Hiérarchie
    parent = django_filters.NumberFilter()
    is_root = django_filters.BooleanFilter(method='filter_is_root')
    level = django_filters.NumberFilter(method='filter_level')
    has_subcategories = django_filters.BooleanFilter(method='filter_has_subcategories')
    
    # Métriques
    websites_count__gte = django_filters.NumberFilter(method='filter_websites_count_gte')
    websites_count__lte = django_filters.NumberFilter(method='filter_websites_count_lte')
    has_websites = django_filters.BooleanFilter(method='filter_has_websites')
    
    # DA ranges
    typical_da_range_min__gte = django_filters.NumberFilter(field_name='typical_da_range_min', lookup_expr='gte')
    typical_da_range_max__lte = django_filters.NumberFilter(field_name='typical_da_range_max', lookup_expr='lte')
    
    # Recherche générale
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = WebsiteCategory
        fields = ['name', 'parent', 'color']
    
    def filter_is_root(self, queryset, name, value):
        """Filtrer les catégories racines"""
        if value:
            return queryset.filter(parent__isnull=True)
        return queryset.filter(parent__isnull=False)
    
    def filter_level(self, queryset, name, value):
        """Filtrer par niveau de hiérarchie"""
        if value == 0:
            return queryset.filter(parent__isnull=True)
        elif value == 1:
            return queryset.filter(parent__isnull=False, parent__parent__isnull=True)
        return queryset.none()
    
    def filter_has_subcategories(self, queryset, name, value):
        """Filtrer les catégories avec/sans sous-catégories"""
        if value:
            return queryset.filter(subcategories__isnull=False).distinct()
        return queryset.filter(subcategories__isnull=True)
    
    def filter_websites_count_gte(self, queryset, name, value):
        """Filtrer par nombre minimum de websites"""
        return queryset.annotate(
            websites_count=models.Count('websites')
        ).filter(websites_count__gte=value)
    
    def filter_websites_count_lte(self, queryset, name, value):
        """Filtrer par nombre maximum de websites"""
        return queryset.annotate(
            websites_count=models.Count('websites')
        ).filter(websites_count__lte=value)
    
    def filter_has_websites(self, queryset, name, value):
        """Filtrer les catégories avec/sans websites"""
        if value:
            return queryset.filter(websites__isnull=False).distinct()
        return queryset.filter(websites__isnull=True)
    
    def filter_search(self, queryset, name, value):
        """Recherche dans nom et description"""
        return queryset.filter(
            models.Q(name__icontains=value) |
            models.Q(description__icontains=value) |
            models.Q(slug__icontains=value)
        )

class WebsiteCategorizationFilter(django_filters.FilterSet):
    """Filtres pour les associations website-catégorie"""
    
    # Relations
    website = django_filters.NumberFilter()
    category = django_filters.NumberFilter()
    categorized_by = django_filters.NumberFilter()
    
    # Propriétés
    is_primary = django_filters.BooleanFilter()
    source = django_filters.ChoiceFilter(choices=WebsiteCategorization.CATEGORIZATION_SOURCE_CHOICES)
    
    # Scores et confiance
    confidence_score__gte = django_filters.NumberFilter(field_name='confidence_score', lookup_expr='gte')
    confidence_score__lte = django_filters.NumberFilter(field_name='confidence_score', lookup_expr='lte')
    has_confidence_score = django_filters.BooleanFilter(method='filter_has_confidence_score')
    
    # Dates
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    # Website filters (via relation)
    website__name = django_filters.CharFilter(field_name='website__name', lookup_expr='icontains')
    website__domain_authority__gte = django_filters.NumberFilter(field_name='website__domain_authority', lookup_expr='gte')
    website__brand = django_filters.NumberFilter(field_name='website__brand')
    
    # Category filters (via relation)
    category__name = django_filters.CharFilter(field_name='category__name', lookup_expr='icontains')
    category__parent = django_filters.NumberFilter(field_name='category__parent')
    category_is_root = django_filters.BooleanFilter(method='filter_category_is_root')
    
    # Recherche générale
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = WebsiteCategorization
        fields = ['website', 'category', 'is_primary', 'source']
    
    def filter_has_confidence_score(self, queryset, name, value):
        """Filtrer les catégorisations avec/sans score de confiance"""
        if value:
            return queryset.filter(confidence_score__isnull=False)
        return queryset.filter(confidence_score__isnull=True)
    
    def filter_category_is_root(self, queryset, name, value):
        """Filtrer par catégories racines ou sous-catégories"""
        if value:
            return queryset.filter(category__parent__isnull=True)
        return queryset.filter(category__parent__isnull=False)
    
    def filter_search(self, queryset, name, value):
        """Recherche dans website, catégorie et notes"""
        return queryset.filter(
            models.Q(website__name__icontains=value) |
            models.Q(category__name__icontains=value) |
            models.Q(notes__icontains=value)
        )