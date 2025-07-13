# backend/seo_pages_seo/filters/seo_filters.py

import django_filters
from django.db import models

from ..models import PageSEO, PagePerformance

class PageSEOFilter(django_filters.FilterSet):
    """Filtres pour configuration SEO des pages"""
    
    page = django_filters.NumberFilter()
    website = django_filters.NumberFilter(field_name='page__website')
    sitemap_changefreq = django_filters.ChoiceFilter(choices=PageSEO.CHANGEFREQ_CHOICES)
    exclude_from_sitemap = django_filters.BooleanFilter()
    
    # Filtres par priorité sitemap
    sitemap_priority__gte = django_filters.NumberFilter(
        field_name='sitemap_priority', 
        lookup_expr='gte'
    )
    sitemap_priority__lte = django_filters.NumberFilter(
        field_name='sitemap_priority', 
        lookup_expr='lte'
    )
    sitemap_priority_high = django_filters.BooleanFilter(method='filter_sitemap_priority_high')
    
    # Filtres par contenu
    has_featured_image = django_filters.BooleanFilter(method='filter_has_featured_image')
    
    # Filtres par type de page
    page_type = django_filters.CharFilter(field_name='page__page_type')
    search_intent = django_filters.CharFilter(field_name='page__search_intent')
    
    # Recherche
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = PageSEO
        fields = ['page', 'sitemap_changefreq', 'exclude_from_sitemap']
    
    def filter_sitemap_priority_high(self, queryset, name, value):
        """Filtre pages avec priorité élevée (>= 0.8)"""
        if value:
            return queryset.filter(sitemap_priority__gte=0.8)
        else:
            return queryset.filter(sitemap_priority__lt=0.8)
    
    def filter_has_featured_image(self, queryset, name, value):
        """Filtre pages avec/sans image featured"""
        if value:
            return queryset.exclude(featured_image__isnull=True).exclude(featured_image='')
        else:
            return queryset.filter(
                models.Q(featured_image__isnull=True) | models.Q(featured_image='')
            )
    
    def filter_search(self, queryset, name, value):
        """Recherche dans titre de page"""
        return queryset.filter(page__title__icontains=value)

class PagePerformanceFilter(django_filters.FilterSet):
    """Filtres pour performance des pages"""
    
    page = django_filters.NumberFilter()
    website = django_filters.NumberFilter(field_name='page__website')
    
    # Filtres par statut de rendu
    needs_regeneration = django_filters.BooleanFilter(method='filter_needs_regeneration')
    never_rendered = django_filters.BooleanFilter(method='filter_never_rendered')
    
    # Filtres par temps de rendu
    render_time_slow = django_filters.BooleanFilter(method='filter_render_time_slow')
    render_time__gte = django_filters.NumberFilter(
        field_name='render_time_ms', 
        lookup_expr='gte'
    )
    render_time__lte = django_filters.NumberFilter(
        field_name='render_time_ms', 
        lookup_expr='lte'
    )
    
    # Filtres par cache
    cache_hits__gte = django_filters.NumberFilter(
        field_name='cache_hits', 
        lookup_expr='gte'
    )
    low_cache_hits = django_filters.BooleanFilter(method='filter_low_cache_hits')
    
    # Filtres par dates
    rendered_after = django_filters.DateTimeFilter(
        field_name='last_rendered_at', 
        lookup_expr='gte'
    )
    rendered_before = django_filters.DateTimeFilter(
        field_name='last_rendered_at', 
        lookup_expr='lte'
    )
    crawled_recently = django_filters.BooleanFilter(method='filter_crawled_recently')
    
    class Meta:
        model = PagePerformance
        fields = ['page']
    
    def filter_needs_regeneration(self, queryset, name, value):
        """Filtre pages nécessitant une régénération"""
        if value:
            return queryset.filter(
                models.Q(last_rendered_at__isnull=True) |
                models.Q(last_rendered_at__lt=models.F('page__updated_at'))
            )
        else:
            return queryset.filter(
                last_rendered_at__isnull=False,
                last_rendered_at__gte=models.F('page__updated_at')
            )
    
    def filter_never_rendered(self, queryset, name, value):
        """Filtre pages jamais rendues"""
        if value:
            return queryset.filter(last_rendered_at__isnull=True)
        else:
            return queryset.filter(last_rendered_at__isnull=False)
    
    def filter_render_time_slow(self, queryset, name, value):
        """Filtre pages avec temps de rendu lent (> 2 secondes)"""
        if value:
            return queryset.filter(render_time_ms__gt=2000)
        else:
            return queryset.filter(render_time_ms__lte=2000)
    
    def filter_low_cache_hits(self, queryset, name, value):
        """Filtre pages avec peu de hits cache (< 10)"""
        if value:
            return queryset.filter(cache_hits__lt=10)
        else:
            return queryset.filter(cache_hits__gte=10)
    
    def filter_crawled_recently(self, queryset, name, value):
        """Filtre pages crawlées récemment (< 7 jours)"""
        from django.utils import timezone
        from datetime import timedelta
        
        week_ago = timezone.now() - timedelta(days=7)
        
        if value:
            return queryset.filter(last_crawled_at__gte=week_ago)
        else:
            return queryset.filter(
                models.Q(last_crawled_at__isnull=True) |
                models.Q(last_crawled_at__lt=week_ago)
            )
