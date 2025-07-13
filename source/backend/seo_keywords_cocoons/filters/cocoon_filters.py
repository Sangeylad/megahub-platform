# backend/seo_keywords_cocoons/filters/cocoon_filters.py

import django_filters
from django.db import models
from django.db.models import Count, Q
from ..models import SemanticCocoon, CocoonCategory

import logging
logger = logging.getLogger(__name__)

class CocoonFilter(django_filters.FilterSet):
    """Filtres avancés pour cocons sémantiques"""
    
    # Recherche textuelle
    search = django_filters.CharFilter(method='filter_search')
    
    # Filtres catégories
    category = django_filters.ModelChoiceFilter(
        field_name='categories',
        queryset=CocoonCategory.objects.all()
    )
    category_name = django_filters.CharFilter(method='filter_category_name')
    
    # Filtres mots-clés
    has_keywords = django_filters.BooleanFilter(method='filter_has_keywords')
    keywords_count_min = django_filters.NumberFilter(method='filter_keywords_count_min')
    keywords_count_max = django_filters.NumberFilter(method='filter_keywords_count_max')
    
    # Filtres synchronisation OpenAI
    needs_sync = django_filters.BooleanFilter(method='filter_needs_sync')
    has_openai_file = django_filters.BooleanFilter(method='filter_has_openai_file')
    storage_type = django_filters.ChoiceFilter(
        field_name='openai_storage_type',
        choices=[('file', 'File'), ('vector_store', 'Vector Store')]
    )
    
    # Filtres temporels
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    updated_after = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='gte')
    
    class Meta:
        model = SemanticCocoon
        fields = ['name', 'openai_storage_type']
    
    def filter_search(self, queryset, name, value):
        """Recherche dans nom, description et catégories"""
        if not value or len(value.strip()) < 2:
            return queryset
            
        search_term = value.strip()
        return queryset.filter(
            Q(name__icontains=search_term) |
            Q(description__icontains=search_term) |
            Q(categories__name__icontains=search_term)
        ).distinct()
    
    def filter_category_name(self, queryset, name, value):
        """Filtre par nom de catégorie (recherche partielle)"""
        if not value:
            return queryset
        return queryset.filter(categories__name__icontains=value).distinct()
    
    def filter_has_keywords(self, queryset, name, value):
        """Filtre par présence de mots-clés"""
        if value:
            return queryset.filter(cocoon_keywords__isnull=False).distinct()
        return queryset.filter(cocoon_keywords__isnull=True)
    
    def filter_keywords_count_min(self, queryset, name, value):
        """Filtre par nombre minimum de mots-clés"""
        try:
            min_count = int(value)
            if min_count < 0:
                return queryset
            return queryset.annotate(
                kw_count=Count('cocoon_keywords', distinct=True)
            ).filter(kw_count__gte=min_count)
        except (ValueError, TypeError):
            logger.warning(f"Invalid keywords_count_min value: {value}")
            return queryset
    
    def filter_keywords_count_max(self, queryset, name, value):
        """Filtre par nombre maximum de mots-clés"""
        try:
            max_count = int(value)
            if max_count < 0:
                return queryset
            return queryset.annotate(
                kw_count=Count('cocoon_keywords', distinct=True)
            ).filter(kw_count__lte=max_count)
        except (ValueError, TypeError):
            logger.warning(f"Invalid keywords_count_max value: {value}")
            return queryset
    
    def filter_needs_sync(self, queryset, name, value):
        """Filtre sur besoin de synchronisation OpenAI"""
        if value:
            # Cocons sans sync OU modifiés depuis dernière sync
            return queryset.filter(
                Q(last_pushed_at__isnull=True) |
                Q(updated_at__gt=models.F('last_pushed_at'))
            )
        else:
            # Cocons synchronisés et à jour
            return queryset.filter(
                last_pushed_at__isnull=False,
                updated_at__lte=models.F('last_pushed_at')
            )
    
    def filter_has_openai_file(self, queryset, name, value):
        """Filtre par présence de fichier OpenAI"""
        if value:
            return queryset.exclude(
                Q(openai_file_id__isnull=True) | Q(openai_file_id='')
            )
        return queryset.filter(
            Q(openai_file_id__isnull=True) | Q(openai_file_id='')
        )