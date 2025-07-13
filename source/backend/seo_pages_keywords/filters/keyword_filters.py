# backend/seo_pages_keywords/filters/keyword_filters.py

import django_filters
from django.db import models

from ..models import PageKeyword

class PageKeywordFilter(django_filters.FilterSet):
    """Filtres pour associations page-keyword"""
    
    page = django_filters.NumberFilter()
    website = django_filters.NumberFilter(field_name='page__website')
    keyword = django_filters.NumberFilter()
    keyword_type = django_filters.ChoiceFilter(choices=PageKeyword.KEYWORD_TYPE_CHOICES)
    source_cocoon = django_filters.NumberFilter()
    is_ai_selected = django_filters.BooleanFilter()
    
    # Filtres par métriques keyword
    keyword_volume__gte = django_filters.NumberFilter(
        field_name='keyword__volume', 
        lookup_expr='gte'
    )
    keyword_volume__lte = django_filters.NumberFilter(
        field_name='keyword__volume', 
        lookup_expr='lte'
    )
    keyword_search_intent = django_filters.CharFilter(field_name='keyword__search_intent')
    
    # Filtres par position
    position__gte = django_filters.NumberFilter(field_name='position', lookup_expr='gte')
    position__lte = django_filters.NumberFilter(field_name='position', lookup_expr='lte')
    has_position = django_filters.BooleanFilter(method='filter_has_position')
    
    # Filtres par source
    from_cocoon = django_filters.BooleanFilter(method='filter_from_cocoon')
    cocoon_name = django_filters.CharFilter(field_name='source_cocoon__name', lookup_expr='icontains')
    
    # Filtres par page
    page_type = django_filters.CharFilter(field_name='page__page_type')
    page_search_intent = django_filters.CharFilter(field_name='page__search_intent')
    
    # Filtres par volume (groupés)
    high_volume = django_filters.BooleanFilter(method='filter_high_volume')
    medium_volume = django_filters.BooleanFilter(method='filter_medium_volume')
    low_volume = django_filters.BooleanFilter(method='filter_low_volume')
    
    # Recherche
    search = django_filters.CharFilter(method='filter_search')
    keyword_search = django_filters.CharFilter(
        field_name='keyword__keyword', 
        lookup_expr='icontains'
    )
    
    class Meta:
        model = PageKeyword
        fields = ['page', 'keyword', 'keyword_type', 'source_cocoon', 'is_ai_selected']
    
    def filter_has_position(self, queryset, name, value):
        """Filtre associations avec/sans position définie"""
        if value:
            return queryset.filter(position__isnull=False)
        else:
            return queryset.filter(position__isnull=True)
    
    def filter_from_cocoon(self, queryset, name, value):
        """Filtre mots-clés issus/non issus d'un cocon"""
        if value:
            return queryset.filter(source_cocoon__isnull=False)
        else:
            return queryset.filter(source_cocoon__isnull=True)
    
    def filter_high_volume(self, queryset, name, value):
        """Filtre mots-clés à fort volume (>= 5000)"""
        if value:
            return queryset.filter(keyword__volume__gte=5000)
        else:
            return queryset.filter(keyword__volume__lt=5000)
    
    def filter_medium_volume(self, queryset, name, value):
        """Filtre mots-clés à volume moyen (1000-4999)"""
        if value:
            return queryset.filter(
                keyword__volume__gte=1000,
                keyword__volume__lt=5000
            )
        else:
            return queryset.exclude(
                keyword__volume__gte=1000,
                keyword__volume__lt=5000
            )
    
    def filter_low_volume(self, queryset, name, value):
        """Filtre mots-clés à faible volume (< 1000)"""
        if value:
            return queryset.filter(keyword__volume__lt=1000)
        else:
            return queryset.filter(keyword__volume__gte=1000)
    
    def filter_search(self, queryset, name, value):
        """Recherche dans keyword et titre de page"""
        return queryset.filter(
            models.Q(keyword__keyword__icontains=value) |
            models.Q(page__title__icontains=value) |
            models.Q(notes__icontains=value)
        )
