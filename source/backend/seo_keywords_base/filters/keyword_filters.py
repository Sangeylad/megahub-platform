# backend/seo_keywords_base/filters/keyword_filters.py

import django_filters
from django.db.models import Q, Exists, OuterRef
from django.db.models.functions import Cast, Replace
from django.db.models import FloatField, Value
from ..models import Keyword

class KeywordFilter(django_filters.FilterSet):
    """
    🎯 FILTRE UNIFIÉ CROSS-APP
    
    Supporte tous les anciens filtres + nouvelles relations
    """
    
    # ===== FILTRES DE BASE =====
    search = django_filters.CharFilter(method='filter_search')
    keyword = django_filters.CharFilter(field_name='keyword', lookup_expr='icontains')
    
    # Volume
    volume_min = django_filters.NumberFilter(field_name='volume', lookup_expr='gte')
    volume_max = django_filters.NumberFilter(field_name='volume', lookup_expr='lte')
    volume__gte = django_filters.NumberFilter(field_name='volume', lookup_expr='gte')  # Alias frontend
    volume__lte = django_filters.NumberFilter(field_name='volume', lookup_expr='lte')  # Alias frontend
    
    # Intention
    search_intent = django_filters.ChoiceFilter(choices=[
        ('TOFU', 'Top of Funnel'),
        ('MOFU', 'Middle of Funnel'),
        ('BOFU', 'Bottom of Funnel')
    ])
    
    # Propriétés booléennes  
    local_pack = django_filters.BooleanFilter()
    youtube_videos = django_filters.CharFilter()
    
    # CPC
    cpc = django_filters.CharFilter()
    cpc_min = django_filters.NumberFilter(method='filter_cpc_gte')
    cpc_max = django_filters.NumberFilter(method='filter_cpc_lte')
    
    # ===== FILTRES CROSS-APP MÉTRIQUES =====
    
    # Domain Authority (toutes variantes)
    da_min__gte = django_filters.NumberFilter(method='filter_da_min_gte')
    da_max__lte = django_filters.NumberFilter(method='filter_da_max_lte')
    da_median__gte = django_filters.NumberFilter(method='filter_da_median_gte')
    da_median__lte = django_filters.NumberFilter(method='filter_da_median_lte')
    da_q1__gte = django_filters.NumberFilter(method='filter_da_q1_gte')
    da_q3__lte = django_filters.NumberFilter(method='filter_da_q3_lte')
    
    # Alias frontend pour rétrocompatibilité
    da_median_min = django_filters.NumberFilter(method='filter_da_median_gte')
    da_median_max = django_filters.NumberFilter(method='filter_da_median_lte')
    
    # Backlinks (toutes variantes)
    bl_min__gte = django_filters.NumberFilter(method='filter_bl_min_gte')
    bl_max__lte = django_filters.NumberFilter(method='filter_bl_max_lte')
    bl_median__gte = django_filters.NumberFilter(method='filter_bl_median_gte')
    bl_median__lte = django_filters.NumberFilter(method='filter_bl_median_lte')
    bl_q1__gte = django_filters.NumberFilter(method='filter_bl_q1_gte')
    bl_q3__lte = django_filters.NumberFilter(method='filter_bl_q3_lte')
    
    # Alias frontend
    bl_median_min = django_filters.NumberFilter(method='filter_bl_median_gte')
    bl_median_max = django_filters.NumberFilter(method='filter_bl_median_lte')
    
    # Difficulté
    kdifficulty_min = django_filters.NumberFilter(method='filter_kdifficulty_gte')
    kdifficulty_max = django_filters.NumberFilter(method='filter_kdifficulty_lte')
    kdifficulty__gte = django_filters.NumberFilter(method='filter_kdifficulty_gte')
    kdifficulty__lte = django_filters.NumberFilter(method='filter_kdifficulty_lte')
    
    # ===== FILTRES CROSS-APP RELATIONS =====
    
    # Cocons
    in_cocoon = django_filters.NumberFilter(method='filter_in_cocoon')
    cocoon_id = django_filters.NumberFilter(method='filter_in_cocoon')  # Alias
    not_in_cocoon = django_filters.NumberFilter(method='filter_not_in_cocoon')
    has_cocoons = django_filters.BooleanFilter(method='filter_has_cocoons')
    
    # PPAs
    has_ppas = django_filters.BooleanFilter(method='filter_has_ppas')
    ppa_position = django_filters.NumberFilter(method='filter_ppa_position')
    
    # Content Types
    content_type = django_filters.CharFilter(method='filter_content_type')
    has_content_types = django_filters.BooleanFilter(method='filter_has_content_types')
    
    # Exclusions
    exclude_page = django_filters.NumberFilter(method='filter_exclude_page')
    
    class Meta:
        model = Keyword
        fields = [
            'volume', 'search_intent', 'local_pack', 'cpc', 'youtube_videos'
        ]
    
    def filter_search(self, queryset, name, value):
        """Recherche textuelle étendue"""
        if not value:
            return queryset
        return queryset.filter(
            Q(keyword__icontains=value) |
            Q(content_types__icontains=value)
        )
    
    # ===== MÉTHODES MÉTRIQUES =====
    
    def filter_da_min_gte(self, queryset, name, value):
        return self._filter_metrics_field(queryset, 'da_min__gte', value)
    
    def filter_da_max_lte(self, queryset, name, value):
        return self._filter_metrics_field(queryset, 'da_max__lte', value)
    
    def filter_da_median_gte(self, queryset, name, value):
        return self._filter_metrics_field(queryset, 'da_median__gte', value)
    
    def filter_da_median_lte(self, queryset, name, value):
        return self._filter_metrics_field(queryset, 'da_median__lte', value)
    
    def filter_da_q1_gte(self, queryset, name, value):
        return self._filter_metrics_field(queryset, 'da_q1__gte', value)
    
    def filter_da_q3_lte(self, queryset, name, value):
        return self._filter_metrics_field(queryset, 'da_q3__lte', value)
    
    def filter_bl_min_gte(self, queryset, name, value):
        return self._filter_metrics_field(queryset, 'bl_min__gte', value)
    
    def filter_bl_max_lte(self, queryset, name, value):
        return self._filter_metrics_field(queryset, 'bl_max__lte', value)
    
    def filter_bl_median_gte(self, queryset, name, value):
        return self._filter_metrics_field(queryset, 'bl_median__gte', value)
    
    def filter_bl_median_lte(self, queryset, name, value):
        return self._filter_metrics_field(queryset, 'bl_median__lte', value)
    
    def filter_bl_q1_gte(self, queryset, name, value):
        return self._filter_metrics_field(queryset, 'bl_q1__gte', value)
    
    def filter_bl_q3_lte(self, queryset, name, value):
        return self._filter_metrics_field(queryset, 'bl_q3__lte', value)
    
    def _filter_metrics_field(self, queryset, filter_expr, value):
        """Helper pour filtrage métriques cross-app"""
        try:
            from seo_keywords_metrics.models import KeywordMetrics
            return queryset.filter(
                Exists(
                    KeywordMetrics.objects.filter(
                        keyword=OuterRef('pk'),
                        **{filter_expr: value}
                    )
                )
            )
        except ImportError:
            return queryset.none()
    
    def filter_kdifficulty_gte(self, queryset, name, value):
        """Filtrage difficulté avec normalisation"""
        try:
            from seo_keywords_metrics.models import KeywordMetrics
            
            # Annotation pour normaliser KD
            normalized_queryset = queryset.annotate(
                kd_normalized=Cast(
                    Replace(
                        Replace('metrics__kdifficulty', Value('%'), Value('')),
                        Value(','), Value('.')
                    ),
                    FloatField()
                )
            )
            
            return normalized_queryset.filter(kd_normalized__gte=value)
        except ImportError:
            return queryset
    
    def filter_kdifficulty_lte(self, queryset, name, value):
        """Filtrage difficulté max avec normalisation"""
        try:
            from seo_keywords_metrics.models import KeywordMetrics
            
            normalized_queryset = queryset.annotate(
                kd_normalized=Cast(
                    Replace(
                        Replace('metrics__kdifficulty', Value('%'), Value('')),
                        Value(','), Value('.')
                    ),
                    FloatField()
                )
            )
            
            return normalized_queryset.filter(kd_normalized__lte=value)
        except ImportError:
            return queryset
    
    def filter_cpc_gte(self, queryset, name, value):
        """Filtrage CPC avec normalisation"""
        cpc_normalized = Cast(
            Replace(
                Replace(
                    Replace('cpc', Value('€'), Value('')),
                    Value(','), Value('.')
                ),
                Value(' '), Value('')
            ),
            FloatField()
        )
        
        return queryset.annotate(
            cpc_normalized=cpc_normalized
        ).filter(cpc_normalized__gte=value)
    
    def filter_cpc_lte(self, queryset, name, value):
        """Filtrage CPC max avec normalisation"""
        cpc_normalized = Cast(
            Replace(
                Replace(
                    Replace('cpc', Value('€'), Value('')),
                    Value(','), Value('.')
                ),
                Value(' '), Value('')
            ),
            FloatField()
        )
        
        return queryset.annotate(
            cpc_normalized=cpc_normalized
        ).filter(cpc_normalized__lte=value)
    
    # ===== MÉTHODES RELATIONS =====
    
    def filter_in_cocoon(self, queryset, name, value):
        """Filtrage par cocon spécifique"""
        try:
            return queryset.filter(cocoon_associations__cocoon_id=value)
        except:
            return queryset.none()
    
    def filter_not_in_cocoon(self, queryset, name, value):
        """Exclusion d'un cocon"""
        try:
            return queryset.exclude(cocoon_associations__cocoon_id=value)
        except:
            return queryset
    
    def filter_has_cocoons(self, queryset, name, value):
        """Filtrage par présence de cocons"""
        if value:
            return queryset.filter(cocoon_associations__isnull=False).distinct()
        else:
            return queryset.filter(cocoon_associations__isnull=True)
    
    def filter_has_ppas(self, queryset, name, value):
        """Filtrage par présence de PPAs"""
        if value:
            return queryset.filter(ppa_associations__isnull=False).distinct()
        else:
            return queryset.filter(ppa_associations__isnull=True)
    
    def filter_ppa_position(self, queryset, name, value):
        """Filtrage par position PPA"""
        try:
            return queryset.filter(ppa_associations__position=value)
        except:
            return queryset.none()
    
    def filter_content_type(self, queryset, name, value):
        """Filtrage par type de contenu"""
        try:
            return queryset.filter(
                Q(content_type_associations__content_type__name__icontains=value) |
                Q(content_types__icontains=value)  # Fallback legacy
            ).distinct()
        except:
            return queryset
    
    def filter_has_content_types(self, queryset, name, value):
        """Filtrage par présence de types de contenu"""
        if value:
            return queryset.filter(
                Q(content_type_associations__isnull=False) |
                Q(content_types__isnull=False, content_types__ne='')
            ).distinct()
        else:
            return queryset.filter(
                content_type_associations__isnull=True,
                content_types__isnull=True
            )
    
    def filter_exclude_page(self, queryset, name, value):
        """Exclusion des mots-clés d'une page (cross-app website)"""
        try:
            # Import dynamique pour éviter circular imports
            from django.apps import apps
            PageKeyword = apps.get_model('website_seo', 'PageKeyword')
            
            used_keywords = PageKeyword.objects.filter(
                page_id=value
            ).values_list('keyword_id', flat=True)
            
            return queryset.exclude(id__in=used_keywords)
        except:
            # Si l'app website n'existe pas encore, pas d'exclusion
            return queryset