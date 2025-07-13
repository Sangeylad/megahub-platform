# backend/seo_websites_core/filters/website_filters.py

import django_filters
from django.db import models
from django.db.models import Count, Q, F, Avg, Max, Min

from ..models import Website

# ===== IMPORTS CROSS-APP SÉCURISÉS =====

# Pages Content
try:
    from seo_pages_content.models import Page
    HAS_PAGES_CONTENT = True
except ImportError:
    HAS_PAGES_CONTENT = False

# Pages Workflow
try:
    from seo_pages_workflow.models import PageStatus
    PAGE_STATUS_CHOICES = PageStatus.PAGE_STATUS_CHOICES
    HAS_WORKFLOW = True
except ImportError:
    PAGE_STATUS_CHOICES = []
    HAS_WORKFLOW = False

# Pages Keywords
try:
    from seo_pages_keywords.models import PageKeyword
    KEYWORD_TYPE_CHOICES = PageKeyword.KEYWORD_TYPE_CHOICES
    HAS_KEYWORDS = True
except ImportError:
    KEYWORD_TYPE_CHOICES = []
    HAS_KEYWORDS = False

# Pages SEO
try:
    from seo_pages_seo.models import PageSEO
    HAS_SEO = True
except ImportError:
    HAS_SEO = False

# Pages Layout
try:
    from seo_pages_layout.models import PageLayout, PageSection
    HAS_LAYOUT = True
except ImportError:
    HAS_LAYOUT = False

# Categorization
try:
    from seo_websites_categorization.models import WebsiteCategory, WebsiteCategorization
    HAS_CATEGORIZATION = True
except ImportError:
    HAS_CATEGORIZATION = False

# Sync Status
try:
    from seo_websites_core.models import WebsiteSyncStatus
    HAS_SYNC = True
except ImportError:
    HAS_SYNC = False

class WebsiteFilter(django_filters.FilterSet):
    """
    🔥 FILTRE WEBSITES CROSS-APP COMPLET
    
    Exemples d'usage :
    GET /websites/?has_published_pages=true&categorization_source=manual&da_above_category=true
    GET /websites/?pages_count_min=50&keywords_coverage_gte=0.8&needs_openai_sync=true
    GET /websites/?primary_category=5&has_page_builder=true&avg_sitemap_priority_gte=0.6
    """
    
    # ===== FILTRES DE BASE (seo_websites_core) =====
    name = django_filters.CharFilter(lookup_expr='icontains')
    url = django_filters.CharFilter(lookup_expr='icontains')
    domain_authority = django_filters.RangeFilter()
    max_competitor_backlinks = django_filters.RangeFilter()
    max_competitor_kd = django_filters.RangeFilter()
    
    # ===== BRAND FILTERS =====
    brand_name = django_filters.CharFilter(
        field_name='brand__name',
        lookup_expr='icontains'
    )
    brand_company = django_filters.NumberFilter(field_name='brand__company')
    has_chatgpt_key = django_filters.BooleanFilter(method='filter_has_chatgpt_key')
    has_gemini_key = django_filters.BooleanFilter(method='filter_has_gemini_key')
    
    # ===== PAGES CONTENT FILTERS =====
    pages_count = django_filters.RangeFilter(method='filter_pages_count')
    has_pages = django_filters.BooleanFilter(method='filter_has_pages')
    page_types = django_filters.CharFilter(method='filter_page_types')
    search_intents = django_filters.CharFilter(method='filter_search_intents')
    has_vitrine_pages = django_filters.BooleanFilter(method='filter_has_vitrine_pages')
    has_blog_pages = django_filters.BooleanFilter(method='filter_has_blog_pages')
    has_product_pages = django_filters.BooleanFilter(method='filter_has_product_pages')
    
    # ===== WORKFLOW FILTERS =====
    has_published_pages = django_filters.BooleanFilter(method='filter_has_published_pages')
    has_draft_pages = django_filters.BooleanFilter(method='filter_has_draft_pages')
    has_scheduled_pages = django_filters.BooleanFilter(method='filter_has_scheduled_pages')
    published_pages_count = django_filters.RangeFilter(method='filter_published_pages_count')
    publication_ratio = django_filters.RangeFilter(method='filter_publication_ratio')
    
    # ===== KEYWORDS FILTERS =====
    has_keywords = django_filters.BooleanFilter(method='filter_has_keywords')
    total_keywords_count = django_filters.RangeFilter(method='filter_total_keywords_count')
    unique_keywords_count = django_filters.RangeFilter(method='filter_unique_keywords_count')
    keywords_coverage = django_filters.RangeFilter(method='filter_keywords_coverage')
    has_primary_keywords = django_filters.BooleanFilter(method='filter_has_primary_keywords')
    ai_keywords_ratio = django_filters.RangeFilter(method='filter_ai_keywords_ratio')
    avg_keyword_volume = django_filters.RangeFilter(method='filter_avg_keyword_volume')
    
    # ===== SEO FILTERS =====
    has_seo_config = django_filters.BooleanFilter(method='filter_has_seo_config')
    has_featured_images = django_filters.BooleanFilter(method='filter_has_featured_images')
    avg_sitemap_priority = django_filters.RangeFilter(method='filter_avg_sitemap_priority')
    excluded_from_sitemap_count = django_filters.RangeFilter(method='filter_excluded_from_sitemap_count')
    meta_description_coverage = django_filters.RangeFilter(method='filter_meta_description_coverage')
    
    # ===== LAYOUT/PAGE BUILDER FILTERS =====
    has_page_builder = django_filters.BooleanFilter(method='filter_has_page_builder')
    sections_count = django_filters.RangeFilter(method='filter_sections_count')
    layout_coverage = django_filters.RangeFilter(method='filter_layout_coverage')
    popular_section_types = django_filters.CharFilter(method='filter_popular_section_types')
    render_strategy = django_filters.ChoiceFilter(
        method='filter_render_strategy',
        choices=[
            ('sections', 'Page Builder'),
            ('markdown', 'Markdown'),
            ('custom', 'Custom Template')
        ]
    )
    
    # ===== CATEGORIZATION FILTERS =====
    website_category = django_filters.ModelChoiceFilter(
        field_name='categorizations__category',
        queryset=None,  # Défini dans __init__
    )
    primary_category = django_filters.ModelChoiceFilter(
        field_name='categorizations__category',
        queryset=None,  # Défini dans __init__
        method='filter_primary_category'
    )
    category_level = django_filters.NumberFilter(method='filter_category_level')
    categorization_source = django_filters.ChoiceFilter(
        field_name='categorizations__source',
        choices=[
            ('manual', 'Manuelle'),
            ('automatic', 'Automatique'),
            ('ai_suggested', 'Suggérée par IA'),
            ('imported', 'Importée'),
        ]
    )
    has_primary_category = django_filters.BooleanFilter(method='filter_has_primary_category')
    
    # ===== PERFORMANCE VS CATEGORY =====
    da_above_category = django_filters.BooleanFilter(method='filter_da_above_category')
    da_below_category = django_filters.BooleanFilter(method='filter_da_below_category')
    pages_above_category = django_filters.BooleanFilter(method='filter_pages_above_category')
    pages_below_category = django_filters.BooleanFilter(method='filter_pages_below_category')
    performance_vs_category = django_filters.ChoiceFilter(
        method='filter_performance_vs_category',
        choices=[
            ('above', 'Au-dessus de la catégorie'),
            ('typical', 'Typique de la catégorie'),
            ('below', 'En-dessous de la catégorie')
        ]
    )
    
    # ===== SYNC & OPENAI FILTERS =====
    needs_openai_sync = django_filters.BooleanFilter(method='filter_needs_openai_sync')
    last_synced_after = django_filters.DateTimeFilter(
        field_name='sync_status__last_openai_sync',
        lookup_expr='gte'
    ) if HAS_SYNC else None
    sync_version = django_filters.NumberFilter(
        field_name='sync_status__openai_sync_version'
    ) if HAS_SYNC else None
    
    # ===== RECHERCHE GLOBALE =====
    search = django_filters.CharFilter(method='filter_search')

    class Meta:
        model = Website
        fields = [
            'name', 'brand', 'domain_authority', 'pages_count',
            'has_published_pages', 'primary_category', 'categorization_source'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Import dynamique pour éviter circular imports
        if HAS_CATEGORIZATION:
            try:
                from seo_websites_categorization.models import WebsiteCategory
                self.filters['website_category'].queryset = WebsiteCategory.objects.all()
                self.filters['primary_category'].queryset = WebsiteCategory.objects.all()
            except ImportError:
                pass

    # ===== BRAND METHODS =====
    
    def filter_has_chatgpt_key(self, queryset, name, value):
        """Sites avec/sans clé ChatGPT"""
        if value:
            return queryset.exclude(
                Q(brand__chatgpt_key__isnull=True) | Q(brand__chatgpt_key='')
            )
        return queryset.filter(
            Q(brand__chatgpt_key__isnull=True) | Q(brand__chatgpt_key='')
        )
    
    def filter_has_gemini_key(self, queryset, name, value):
        """Sites avec/sans clé Gemini"""
        if value:
            return queryset.exclude(
                Q(brand__gemini_key__isnull=True) | Q(brand__gemini_key='')
            )
        return queryset.filter(
            Q(brand__gemini_key__isnull=True) | Q(brand__gemini_key='')
        )
    
    # ===== PAGES CONTENT METHODS =====
    
    def filter_pages_count(self, queryset, name, value):
        """Nombre de pages du site"""
        if not HAS_PAGES_CONTENT:
            return queryset
        
        queryset = queryset.annotate(
            total_pages=Count('pages', distinct=True)
        )
        
        if value.start is not None:
            queryset = queryset.filter(total_pages__gte=value.start)
        if value.stop is not None:
            queryset = queryset.filter(total_pages__lte=value.stop)
        
        return queryset
    
    def filter_has_pages(self, queryset, name, value):
        """Sites avec/sans pages"""
        if not HAS_PAGES_CONTENT:
            return queryset
        
        if value:
            return queryset.filter(pages__isnull=False).distinct()
        return queryset.filter(pages__isnull=True)
    
    def filter_page_types(self, queryset, name, value):
        """Sites ayant certains types de pages (comma-separated)"""
        if not HAS_PAGES_CONTENT:
            return queryset
        
        types = [t.strip() for t in value.split(',')]
        return queryset.filter(pages__page_type__in=types).distinct()
    
    def filter_search_intents(self, queryset, name, value):
        """Sites ayant certaines intentions (comma-separated)"""
        if not HAS_PAGES_CONTENT:
            return queryset
        
        intents = [i.strip() for i in value.split(',')]
        return queryset.filter(pages__search_intent__in=intents).distinct()
    
    def filter_has_vitrine_pages(self, queryset, name, value):
        """Sites avec/sans pages vitrine"""
        if not HAS_PAGES_CONTENT:
            return queryset
        
        if value:
            return queryset.filter(pages__page_type='vitrine').distinct()
        return queryset.exclude(pages__page_type='vitrine')
    
    def filter_has_blog_pages(self, queryset, name, value):
        """Sites avec/sans pages blog"""
        if not HAS_PAGES_CONTENT:
            return queryset
        
        if value:
            return queryset.filter(pages__page_type='blog').distinct()
        return queryset.exclude(pages__page_type='blog')
    
    def filter_has_product_pages(self, queryset, name, value):
        """Sites avec/sans pages produit"""
        if not HAS_PAGES_CONTENT:
            return queryset
        
        if value:
            return queryset.filter(pages__page_type='produit').distinct()
        return queryset.exclude(pages__page_type='produit')
    
    # ===== WORKFLOW METHODS =====
    
    def filter_has_published_pages(self, queryset, name, value):
        """Sites avec/sans pages publiées"""
        if not HAS_WORKFLOW:
            return queryset
        
        if value:
            return queryset.filter(
                pages__workflow_status__status='published'
            ).distinct()
        return queryset.exclude(
            pages__workflow_status__status='published'
        )
    
    def filter_has_draft_pages(self, queryset, name, value):
        """Sites avec/sans brouillons"""
        if not HAS_WORKFLOW:
            return queryset
        
        if value:
            return queryset.filter(
                pages__workflow_status__status='draft'
            ).distinct()
        return queryset.exclude(
            pages__workflow_status__status='draft'
        )
    
    def filter_has_scheduled_pages(self, queryset, name, value):
        """Sites avec/sans pages programmées"""
        if not HAS_WORKFLOW:
            return queryset
        
        if value:
            return queryset.filter(
                pages__workflow_status__status='scheduled'
            ).distinct()
        return queryset.exclude(
            pages__workflow_status__status='scheduled'
        )
    
    def filter_published_pages_count(self, queryset, name, value):
        """Nombre de pages publiées"""
        if not HAS_WORKFLOW:
            return queryset
        
        queryset = queryset.annotate(
            published_count=Count(
                'pages',
                filter=Q(pages__workflow_status__status='published'),
                distinct=True
            )
        )
        
        if value.start is not None:
            queryset = queryset.filter(published_count__gte=value.start)
        if value.stop is not None:
            queryset = queryset.filter(published_count__lte=value.stop)
        
        return queryset
    
    def filter_publication_ratio(self, queryset, name, value):
        """Ratio pages publiées / total pages"""
        if not (HAS_WORKFLOW and HAS_PAGES_CONTENT):
            return queryset
        
        queryset = queryset.annotate(
            total_pages=Count('pages', distinct=True),
            published_pages=Count(
                'pages',
                filter=Q(pages__workflow_status__status='published'),
                distinct=True
            )
        ).annotate(
            pub_ratio=models.Case(
                models.When(total_pages=0, then=0),
                default=models.F('published_pages') * 1.0 / models.F('total_pages'),
                output_field=models.FloatField()
            )
        )
        
        if value.start is not None:
            queryset = queryset.filter(pub_ratio__gte=value.start)
        if value.stop is not None:
            queryset = queryset.filter(pub_ratio__lte=value.stop)
        
        return queryset
    
    # ===== KEYWORDS METHODS =====
    
    def filter_has_keywords(self, queryset, name, value):
        """Sites avec/sans mots-clés"""
        if not HAS_KEYWORDS:
            return queryset
        
        if value:
            return queryset.filter(
                pages__page_keywords__isnull=False
            ).distinct()
        return queryset.filter(
            pages__page_keywords__isnull=True
        )
    
    def filter_total_keywords_count(self, queryset, name, value):
        """Nombre total de mots-clés (avec duplicates)"""
        if not HAS_KEYWORDS:
            return queryset
        
        queryset = queryset.annotate(
            total_keywords=Count('pages__page_keywords', distinct=True)
        )
        
        if value.start is not None:
            queryset = queryset.filter(total_keywords__gte=value.start)
        if value.stop is not None:
            queryset = queryset.filter(total_keywords__lte=value.stop)
        
        return queryset
    
    def filter_unique_keywords_count(self, queryset, name, value):
        """Nombre de mots-clés uniques"""
        if not HAS_KEYWORDS:
            return queryset
        
        queryset = queryset.annotate(
            unique_keywords=Count(
                'pages__page_keywords__keyword',
                distinct=True
            )
        )
        
        if value.start is not None:
            queryset = queryset.filter(unique_keywords__gte=value.start)
        if value.stop is not None:
            queryset = queryset.filter(unique_keywords__lte=value.stop)
        
        return queryset
    
    def filter_keywords_coverage(self, queryset, name, value):
        """Ratio pages avec mots-clés / total pages"""
        if not (HAS_KEYWORDS and HAS_PAGES_CONTENT):
            return queryset
        
        queryset = queryset.annotate(
            total_pages=Count('pages', distinct=True),
            pages_with_keywords=Count(
                'pages',
                filter=Q(pages__page_keywords__isnull=False),
                distinct=True
            )
        ).annotate(
            coverage=models.Case(
                models.When(total_pages=0, then=0),
                default=models.F('pages_with_keywords') * 1.0 / models.F('total_pages'),
                output_field=models.FloatField()
            )
        )
        
        if value.start is not None:
            queryset = queryset.filter(coverage__gte=value.start)
        if value.stop is not None:
            queryset = queryset.filter(coverage__lte=value.stop)
        
        return queryset
    
    def filter_has_primary_keywords(self, queryset, name, value):
        """Sites avec/sans mots-clés primaires"""
        if not HAS_KEYWORDS:
            return queryset
        
        if value:
            return queryset.filter(
                pages__page_keywords__keyword_type='primary'
            ).distinct()
        return queryset.exclude(
            pages__page_keywords__keyword_type='primary'
        )
    
    def filter_ai_keywords_ratio(self, queryset, name, value):
        """Ratio mots-clés sélectionnés par IA"""
        if not HAS_KEYWORDS:
            return queryset
        
        queryset = queryset.annotate(
            total_kw=Count('pages__page_keywords', distinct=True),
            ai_kw=Count(
                'pages__page_keywords',
                filter=Q(pages__page_keywords__is_ai_selected=True),
                distinct=True
            )
        ).annotate(
            ai_ratio=models.Case(
                models.When(total_kw=0, then=0),
                default=models.F('ai_kw') * 1.0 / models.F('total_kw'),
                output_field=models.FloatField()
            )
        )
        
        if value.start is not None:
            queryset = queryset.filter(ai_ratio__gte=value.start)
        if value.stop is not None:
            queryset = queryset.filter(ai_ratio__lte=value.stop)
        
        return queryset
    
    def filter_avg_keyword_volume(self, queryset, name, value):
        """Volume moyen des mots-clés"""
        if not HAS_KEYWORDS:
            return queryset
        
        queryset = queryset.annotate(
            avg_volume=Avg('pages__page_keywords__keyword__volume')
        )
        
        if value.start is not None:
            queryset = queryset.filter(avg_volume__gte=value.start)
        if value.stop is not None:
            queryset = queryset.filter(avg_volume__lte=value.stop)
        
        return queryset
    
    # ===== SEO METHODS =====
    
    def filter_has_seo_config(self, queryset, name, value):
        """Sites avec/sans config SEO"""
        if not HAS_SEO:
            return queryset
        
        if value:
            return queryset.filter(pages__seo_config__isnull=False).distinct()
        return queryset.filter(pages__seo_config__isnull=True)
    
    def filter_has_featured_images(self, queryset, name, value):
        """Sites avec/sans images featured"""
        if not HAS_SEO:
            return queryset
        
        if value:
            return queryset.exclude(
                Q(pages__seo_config__featured_image__isnull=True) |
                Q(pages__seo_config__featured_image='')
            ).distinct()
        return queryset.filter(
            Q(pages__seo_config__featured_image__isnull=True) |
            Q(pages__seo_config__featured_image='')
        ).distinct()
    
    def filter_avg_sitemap_priority(self, queryset, name, value):
        """Priorité sitemap moyenne"""
        if not HAS_SEO:
            return queryset
        
        queryset = queryset.annotate(
            avg_priority=Avg('pages__seo_config__sitemap_priority')
        )
        
        if value.start is not None:
            queryset = queryset.filter(avg_priority__gte=value.start)
        if value.stop is not None:
            queryset = queryset.filter(avg_priority__lte=value.stop)
        
        return queryset
    
    def filter_excluded_from_sitemap_count(self, queryset, name, value):
        """Nombre de pages exclues du sitemap"""
        if not HAS_SEO:
            return queryset
        
        queryset = queryset.annotate(
            excluded_count=Count(
                'pages',
                filter=Q(pages__seo_config__exclude_from_sitemap=True),
                distinct=True
            )
        )
        
        if value.start is not None:
            queryset = queryset.filter(excluded_count__gte=value.start)
        if value.stop is not None:
            queryset = queryset.filter(excluded_count__lte=value.stop)
        
        return queryset
    
    def filter_meta_description_coverage(self, queryset, name, value):
        """Ratio pages avec meta description"""
        if not HAS_PAGES_CONTENT:
            return queryset
        
        queryset = queryset.annotate(
            total_pages=Count('pages', distinct=True),
            pages_with_meta=Count(
                'pages',
                filter=~Q(pages__meta_description__isnull=True) & ~Q(pages__meta_description=''),
                distinct=True
            )
        ).annotate(
            meta_coverage=models.Case(
                models.When(total_pages=0, then=0),
                default=models.F('pages_with_meta') * 1.0 / models.F('total_pages'),
                output_field=models.FloatField()
            )
        )
        
        if value.start is not None:
            queryset = queryset.filter(meta_coverage__gte=value.start)
        if value.stop is not None:
            queryset = queryset.filter(meta_coverage__lte=value.stop)
        
        return queryset
    
    # ===== LAYOUT METHODS =====
    
    def filter_has_page_builder(self, queryset, name, value):
        """Sites avec/sans page builder"""
        if not HAS_LAYOUT:
            return queryset
        
        if value:
            return queryset.filter(
                pages__layout_config__isnull=False
            ).distinct()
        return queryset.filter(
            pages__layout_config__isnull=True
        )
    
    def filter_sections_count(self, queryset, name, value):
        """Nombre de sections page builder"""
        if not HAS_LAYOUT:
            return queryset
        
        queryset = queryset.annotate(
            total_sections=Count('pages__sections', distinct=True)
        )
        
        if value.start is not None:
            queryset = queryset.filter(total_sections__gte=value.start)
        if value.stop is not None:
            queryset = queryset.filter(total_sections__lte=value.stop)
        
        return queryset
    
    def filter_layout_coverage(self, queryset, name, value):
        """Ratio pages avec layout / total pages"""
        if not (HAS_LAYOUT and HAS_PAGES_CONTENT):
            return queryset
        
        queryset = queryset.annotate(
            total_pages=Count('pages', distinct=True),
            pages_with_layout=Count(
                'pages',
                filter=Q(pages__layout_config__isnull=False),
                distinct=True
            )
        ).annotate(
            layout_coverage=models.Case(
                models.When(total_pages=0, then=0),
                default=models.F('pages_with_layout') * 1.0 / models.F('total_pages'),
                output_field=models.FloatField()
            )
        )
        
        if value.start is not None:
            queryset = queryset.filter(layout_coverage__gte=value.start)
        if value.stop is not None:
            queryset = queryset.filter(layout_coverage__lte=value.stop)
        
        return queryset
    
    def filter_popular_section_types(self, queryset, name, value):
        """Sites utilisant certains types de sections (comma-separated)"""
        if not HAS_LAYOUT:
            return queryset
        
        types = [t.strip() for t in value.split(',')]
        return queryset.filter(
            pages__sections__section_type__in=types
        ).distinct()
    
    def filter_render_strategy(self, queryset, name, value):
        """Sites par stratégie de rendu"""
        if not HAS_LAYOUT:
            return queryset
        
        return queryset.filter(
            pages__layout_config__render_strategy=value
        ).distinct()
    
    # ===== CATEGORIZATION METHODS =====
    
    def filter_primary_category(self, queryset, name, value):
        """Sites avec cette catégorie PRINCIPALE"""
        if not HAS_CATEGORIZATION:
            return queryset
        
        return queryset.filter(
            categorizations__category=value,
            categorizations__is_primary=True
        ).distinct()
    
    def filter_category_level(self, queryset, name, value):
        """Sites selon niveau de catégorie"""
        if not HAS_CATEGORIZATION:
            return queryset
        
        try:
            from seo_websites_categorization.models import WebsiteCategory
            
            if value == 0:
                # Catégories racines
                categories_at_level = WebsiteCategory.objects.filter(parent__isnull=True)
            else:
                # Catégories de niveau N (logique récursive si nécessaire)
                categories_at_level = WebsiteCategory.objects.filter(parent__isnull=False)
            
            return queryset.filter(
                categorizations__category__in=categories_at_level
            ).distinct()
        except ImportError:
            return queryset
    
    def filter_has_primary_category(self, queryset, name, value):
        """Sites avec/sans catégorie principale"""
        if not HAS_CATEGORIZATION:
            return queryset
        
        if value:
            return queryset.filter(
                categorizations__is_primary=True
            ).distinct()
        return queryset.exclude(
            categorizations__is_primary=True
        )
    
    # ===== PERFORMANCE VS CATEGORY METHODS =====
    
    def filter_da_above_category(self, queryset, name, value):
        """Sites avec DA supérieur au typique de leur catégorie"""
        if not (value and HAS_CATEGORIZATION):
            return queryset
        
        return queryset.filter(
            domain_authority__gt=F(
                'categorizations__category__typical_da_range_max'
            ),
            categorizations__is_primary=True
        ).distinct()
    
    def filter_da_below_category(self, queryset, name, value):
        """Sites avec DA inférieur au typique de leur catégorie"""
        if not (value and HAS_CATEGORIZATION):
            return queryset
        
        return queryset.filter(
            domain_authority__lt=F(
                'categorizations__category__typical_da_range_min'
            ),
            categorizations__is_primary=True
        ).distinct()
    
    def filter_pages_above_category(self, queryset, name, value):
        """Sites avec plus de pages que le typique de leur catégorie"""
        if not (value and HAS_CATEGORIZATION and HAS_PAGES_CONTENT):
            return queryset
        
        return queryset.annotate(
            pages_count=Count('pages', distinct=True)
        ).filter(
            pages_count__gt=F(
                'categorizations__category__typical_pages_count'
            ),
            categorizations__is_primary=True
        ).distinct()
    
    def filter_pages_below_category(self, queryset, name, value):
        """Sites avec moins de pages que le typique de leur catégorie"""
        if not (value and HAS_CATEGORIZATION and HAS_PAGES_CONTENT):
            return queryset
        
        return queryset.annotate(
            pages_count=Count('pages', distinct=True)
        ).filter(
            pages_count__lt=F(
                'categorizations__category__typical_pages_count'
            ),
            categorizations__is_primary=True
        ).distinct()
    
    def filter_performance_vs_category(self, queryset, name, value):
        """Performance globale vs catégorie"""
        if not HAS_CATEGORIZATION:
            return queryset
        
        # Logique complexe combinant DA + pages count
        if value == 'above':
            return queryset.filter(
                Q(domain_authority__gt=F('categorizations__category__typical_da_range_max')) |
                Q(pages_count__gt=F('categorizations__category__typical_pages_count')),
                categorizations__is_primary=True
            ).annotate(
                pages_count=Count('pages', distinct=True)
            ).distinct()
        elif value == 'below':
            return queryset.filter(
                domain_authority__lt=F('categorizations__category__typical_da_range_min'),
                categorizations__is_primary=True
            ).annotate(
                pages_count=Count('pages', distinct=True)
            ).distinct()
        elif value == 'typical':
            return queryset.filter(
                domain_authority__gte=F('categorizations__category__typical_da_range_min'),
                domain_authority__lte=F('categorizations__category__typical_da_range_max'),
                categorizations__is_primary=True
            ).annotate(
                pages_count=Count('pages', distinct=True)
            ).distinct()
        
        return queryset
    
    # ===== SYNC METHODS =====
    
    def filter_needs_openai_sync(self, queryset, name, value):
        """Sites nécessitant synchronisation OpenAI"""
        if not HAS_SYNC:
            return queryset
        
        if value:
            return queryset.filter(
                Q(sync_status__last_openai_sync__isnull=True) |
                Q(sync_status__last_openai_sync__lt=F('updated_at'))
            )
        return queryset.filter(
            sync_status__last_openai_sync__isnull=False,
            sync_status__last_openai_sync__gte=F('updated_at')
        )
    
    # ===== RECHERCHE GLOBALE =====
    
    def filter_search(self, queryset, name, value):
        """Recherche dans nom, URL, brand"""
        return queryset.filter(
            Q(name__icontains=value) |
            Q(url__icontains=value) |
            Q(brand__name__icontains=value)
        )
        
    # ===== DESIGN SYSTEM FILTERS =====

    # Colors Config
    has_color_config = django_filters.BooleanFilter(method='filter_has_color_config')
    primary_color = django_filters.CharFilter(
        field_name='color_config__primary_override',
        lookup_expr='icontains'
    )
    has_brand_colors = django_filters.BooleanFilter(method='filter_has_brand_colors')

    # Typography Config  
    has_typography_config = django_filters.BooleanFilter(method='filter_has_typography_config')
    font_primary_override = django_filters.CharFilter(
        field_name='typography_config__font_primary_override',
        lookup_expr='icontains'
    )
    base_font_size_range = django_filters.RangeFilter(
        field_name='typography_config__base_font_size_override'
    )

    # Spacing/Layout Config
    has_layout_config = django_filters.BooleanFilter(method='filter_has_layout_config')
    max_width_override = django_filters.CharFilter(
        field_name='layout_config__max_width_override'
    )
    sidebar_width_range = django_filters.RangeFilter(
        field_name='layout_config__sidebar_width'
    )
    nav_collapse_breakpoint = django_filters.ChoiceFilter(
        field_name='layout_config__nav_collapse_breakpoint',
        choices=[('sm', 'Small'), ('md', 'Medium'), ('lg', 'Large')]
    )

    # Tailwind Config  
    has_tailwind_config = django_filters.BooleanFilter(method='filter_has_tailwind_config')
    needs_tailwind_regeneration = django_filters.BooleanFilter(method='filter_needs_tailwind_regeneration')
    tailwind_last_generated_after = django_filters.DateTimeFilter(
        field_name='tailwind_config__last_generated_at',
        lookup_expr='gte'
    )

    # Design Completeness
    design_completeness = django_filters.ChoiceFilter(
        method='filter_design_completeness',
        choices=[
            ('basic', 'Config de base seulement'),
            ('partial', 'Partiellement configuré'),
            ('complete', 'Design system complet'),
            ('custom', 'Entièrement personnalisé')
        ]
    )
    
    # ===== DESIGN SYSTEM METHODS =====

    def filter_has_color_config(self, queryset, name, value):
        """Sites avec/sans config couleurs personnalisée"""
        if value:
            return queryset.filter(color_config__isnull=False)
        return queryset.filter(color_config__isnull=True)

    def filter_has_brand_colors(self, queryset, name, value):
        """Sites utilisant les couleurs de la brand (pas d'override)"""
        if value:
            return queryset.filter(
                color_config__isnull=False,
                color_config__primary_override__isnull=True,
                color_config__secondary_override__isnull=True
            )
        return queryset.filter(
            Q(color_config__primary_override__isnull=False) |
            Q(color_config__secondary_override__isnull=False)
        )

    def filter_has_typography_config(self, queryset, name, value):
        """Sites avec/sans config typo personnalisée"""
        if value:
            return queryset.filter(typography_config__isnull=False)
        return queryset.filter(typography_config__isnull=True)

    def filter_has_layout_config(self, queryset, name, value):
        """Sites avec/sans config layout personnalisée"""
        if value:
            return queryset.filter(layout_config__isnull=False)
        return queryset.filter(layout_config__isnull=True)

    def filter_has_tailwind_config(self, queryset, name, value):
        """Sites avec/sans config Tailwind générée"""
        if value:
            return queryset.filter(tailwind_config__isnull=False)
        return queryset.filter(tailwind_config__isnull=True)

    def filter_needs_tailwind_regeneration(self, queryset, name, value):
        """Sites nécessitant régénération Tailwind"""
        if value:
            return queryset.filter(
                Q(tailwind_config__last_generated_at__isnull=True) |
                Q(tailwind_config__last_generated_at__lt=F('updated_at'))
            )
        return queryset.filter(
            tailwind_config__last_generated_at__isnull=False,
            tailwind_config__last_generated_at__gte=F('updated_at')
        )

    def filter_design_completeness(self, queryset, name, value):
        """Sites selon niveau de personnalisation design"""
        if value == 'basic':
            # Seules configs brand, pas d'overrides
            return queryset.filter(
                brand__color_palette__isnull=False,
                color_config__isnull=True,
                typography_config__isnull=True,
                layout_config__isnull=True
            )
        elif value == 'partial':
            # Quelques overrides mais pas complet
            return queryset.filter(
                Q(color_config__isnull=False) | 
                Q(typography_config__isnull=False) |
                Q(layout_config__isnull=False)
            ).exclude(
                color_config__isnull=False,
                typography_config__isnull=False, 
                layout_config__isnull=False,
                tailwind_config__isnull=False
            )
        elif value == 'complete':
            # Toutes les configs présentes
            return queryset.filter(
                color_config__isnull=False,
                typography_config__isnull=False,
                layout_config__isnull=False,
                tailwind_config__isnull=False
            )
        elif value == 'custom':
            # Beaucoup d'overrides = très personnalisé
            return queryset.filter(
                Q(color_config__primary_override__isnull=False) |
                Q(color_config__secondary_override__isnull=False) |
                Q(typography_config__font_primary_override__isnull=False) |
                Q(layout_config__max_width_override__isnull=False)
            )
        
        return queryset