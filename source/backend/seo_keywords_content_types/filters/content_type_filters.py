# backend/seo_keywords_content_types/filters/content_type_filters.py

import django_filters
from ..models import ContentType, KeywordContentType


class ContentTypeFilter(django_filters.FilterSet):
    """Filtres pour types de contenu"""
    
    # Recherche dans nom et description
    search = django_filters.CharFilter(method='filter_search')
    
    # Filtre sur présence de mots-clés
    has_keywords = django_filters.BooleanFilter(method='filter_has_keywords')
    
    def filter_search(self, queryset, name, value):
        """Recherche dans nom et description"""
        from django.db.models import Q
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value)
        )
    
    def filter_has_keywords(self, queryset, name, value):
        """Filtre sur présence de mots-clés associés"""
        if value:
            return queryset.filter(keyword_associations__isnull=False).distinct()
        return queryset.filter(keyword_associations__isnull=True)
    
    class Meta:
        model = ContentType
        fields = ['name']


class KeywordContentTypeFilter(django_filters.FilterSet):
    """Filtres pour associations keyword-content type"""
    
    # Filtre par mot-clé
    keyword_search = django_filters.CharFilter(
        field_name='keyword__keyword',
        lookup_expr='icontains'
    )
    
    # Filtre par type de contenu
    content_type_search = django_filters.CharFilter(
        field_name='content_type__name',
        lookup_expr='icontains'
    )
    
    # Filtre par priorité
    priority_min = django_filters.NumberFilter(field_name='priority', lookup_expr='gte')
    priority_max = django_filters.NumberFilter(field_name='priority', lookup_expr='lte')
    
    # Filtre par volume du mot-clé
    keyword_volume_min = django_filters.NumberFilter(
        field_name='keyword__volume',
        lookup_expr='gte'
    )
    
    class Meta:
        model = KeywordContentType
        fields = ['priority', 'keyword', 'content_type']