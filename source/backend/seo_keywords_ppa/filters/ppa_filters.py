# backend/seo_keywords_ppa/filters/ppa_filters.py

import django_filters
from django.db import models
from ..models import PPA, KeywordPPA


class PPAFilter(django_filters.FilterSet):
    """Filtres pour questions PPA"""
    
    # Recherche dans la question
    search = django_filters.CharFilter(
        field_name='question',
        lookup_expr='icontains'
    )
    
    # Filtre par nombre de mots-clés associés
    has_keywords = django_filters.BooleanFilter(method='filter_has_keywords')
    
    def filter_has_keywords(self, queryset, name, value):
        """Filtre sur présence de mots-clés associés"""
        if value:
            return queryset.filter(keyword_associations__isnull=False).distinct()
        return queryset.filter(keyword_associations__isnull=True)
    
    class Meta:
        model = PPA
        fields = ['question']


class KeywordPPAFilter(django_filters.FilterSet):
    """Filtres pour associations keyword-PPA"""
    
    # Filtre par position
    position = django_filters.NumberFilter()
    position_gte = django_filters.NumberFilter(field_name='position', lookup_expr='gte')
    position_lte = django_filters.NumberFilter(field_name='position', lookup_expr='lte')
    
    # Filtre par mot-clé
    keyword_search = django_filters.CharFilter(
        field_name='keyword__keyword',
        lookup_expr='icontains'
    )
    
    # Filtre par question PPA
    ppa_search = django_filters.CharFilter(
        field_name='ppa__question',
        lookup_expr='icontains'
    )
    
    # Filtre par volume du mot-clé
    keyword_volume_min = django_filters.NumberFilter(
        field_name='keyword__volume',
        lookup_expr='gte'
    )
    keyword_volume_max = django_filters.NumberFilter(
        field_name='keyword__volume',
        lookup_expr='lte'
    )
    
    class Meta:
        model = KeywordPPA
        fields = ['position', 'keyword', 'ppa']