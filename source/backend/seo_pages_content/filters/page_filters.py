# backend/seo_pages_content/filters/page_filters.py

import django_filters
from django.db import models
from django.db.models import Count, Q

from ..models import Page

# ===== IMPORTS CROSS-APP SÉCURISÉS =====

# Workflow
try:
    from seo_pages_workflow.models import PageStatus
    WORKFLOW_STATUS_CHOICES = PageStatus.PAGE_STATUS_CHOICES
    HAS_WORKFLOW = True
except ImportError:
    WORKFLOW_STATUS_CHOICES = []
    HAS_WORKFLOW = False

# Keywords
try:
    from seo_pages_keywords.models import PageKeyword
    KEYWORD_TYPE_CHOICES = PageKeyword.KEYWORD_TYPE_CHOICES
    HAS_KEYWORDS = True
except ImportError:
    KEYWORD_TYPE_CHOICES = []
    HAS_KEYWORDS = False

# SEO - pas besoin d'import, les choices sont dans le modèle
HAS_SEO = True  # Toujours présent car dans la même base

# Layout - pas besoin d'import, les choices sont dans le modèle
HAS_LAYOUT = True  # Toujours présent car dans la même base

class PageFilter(django_filters.FilterSet):
    """
    🔥 FILTRE PAGES CROSS-APP COMPLET
    
    Exemples d'usage :
    GET /pages/?workflow_status=published&has_keywords=true&hierarchy_level=2
    GET /pages/?page_type=blog&sitemap_priority_min=0.7&keyword_type=primary
    """
    
    # ===== FILTRES DE BASE (seo_pages_content) =====
    title = django_filters.CharFilter(lookup_expr='icontains')
    url_path = django_filters.CharFilter(lookup_expr='icontains')
    website = django_filters.NumberFilter()
    page_type = django_filters.ChoiceFilter(choices=Page.PAGE_TYPE_CHOICES)
    search_intent = django_filters.ChoiceFilter(choices=Page.SEARCH_INTENT_CHOICES)
    has_meta_description = django_filters.BooleanFilter(method='filter_has_meta_description')
    
    # ===== WORKFLOW (seo_pages_workflow) =====
    workflow_status = django_filters.ChoiceFilter(
        field_name='workflow_status__status',
        choices=WORKFLOW_STATUS_CHOICES
    ) if HAS_WORKFLOW else None
    
    is_published = django_filters.BooleanFilter(method='filter_is_published')
    is_scheduled = django_filters.BooleanFilter(method='filter_is_scheduled')
    status_changed_after = django_filters.DateTimeFilter(
        field_name='workflow_status__status_changed_at',
        lookup_expr='gte'
    ) if HAS_WORKFLOW else None
    
    # ===== HIÉRARCHIE (seo_pages_hierarchy) =====
    hierarchy_level = django_filters.NumberFilter(method='filter_hierarchy_level')
    has_parent = django_filters.BooleanFilter(method='filter_has_parent')
    has_children = django_filters.BooleanFilter(method='filter_has_children')
    is_root_page = django_filters.BooleanFilter(method='filter_is_root_page')
    
    # ===== KEYWORDS (seo_pages_keywords) =====
    has_keywords = django_filters.BooleanFilter(method='filter_has_keywords')
    keywords_count = django_filters.RangeFilter(method='filter_keywords_count')
    has_primary_keyword = django_filters.BooleanFilter(method='filter_has_primary_keyword')
    keyword_type = django_filters.ChoiceFilter(
        field_name='page_keywords__keyword_type',
        choices=KEYWORD_TYPE_CHOICES
    ) if HAS_KEYWORDS else None
    is_ai_selected = django_filters.BooleanFilter(
        field_name='page_keywords__is_ai_selected'
    ) if HAS_KEYWORDS else None
    
    # ===== SEO (seo_pages_seo) =====
    sitemap_priority = django_filters.RangeFilter(field_name='seo_config__sitemap_priority')
    sitemap_changefreq = django_filters.ChoiceFilter(
        field_name='seo_config__sitemap_changefreq',
        choices=[
            ('always', 'Always'), ('hourly', 'Hourly'), ('daily', 'Daily'),
            ('weekly', 'Weekly'), ('monthly', 'Monthly'), ('yearly', 'Yearly'), ('never', 'Never')
        ]
    )
    has_featured_image = django_filters.BooleanFilter(method='filter_has_featured_image')
    exclude_from_sitemap = django_filters.BooleanFilter(field_name='seo_config__exclude_from_sitemap')
    
    # ===== LAYOUT / PAGE BUILDER (seo_pages_layout) =====
    has_layout = django_filters.BooleanFilter(method='filter_has_layout')
    render_strategy = django_filters.ChoiceFilter(
        field_name='layout_config__render_strategy',
        choices=[('sections', 'Page Builder Sections'), ('markdown', 'Markdown Content'), ('custom', 'Custom Template')]
    )
    has_sections = django_filters.BooleanFilter(method='filter_has_sections')
    sections_count = django_filters.RangeFilter(method='filter_sections_count')
    section_type = django_filters.CharFilter(field_name='sections__section_type')
    
    # ===== PERFORMANCE (seo_pages_seo) =====
    needs_regeneration = django_filters.BooleanFilter(method='filter_needs_regeneration')
    last_rendered_after = django_filters.DateTimeFilter(
        field_name='performance__last_rendered_at',
        lookup_expr='gte'
    )
    
    # ===== RECHERCHE GLOBALE =====
    search = django_filters.CharFilter(method='filter_search')

    class Meta:
        model = Page
        fields = [
            'website', 'page_type', 'search_intent', 'workflow_status',
            'hierarchy_level', 'keyword_type', 'sitemap_changefreq'
        ]

    # ===== MÉTHODES DE FILTRAGE =====
    
    def filter_has_meta_description(self, queryset, name, value):
        """Pages avec/sans meta description"""
        if value:
            return queryset.exclude(
                Q(meta_description__isnull=True) | Q(meta_description='')
            )
        return queryset.filter(
            Q(meta_description__isnull=True) | Q(meta_description='')
        )
    
    # === WORKFLOW METHODS ===
    
    def filter_is_published(self, queryset, name, value):
        """Pages publiées (status = 'published')"""
        if not HAS_WORKFLOW:
            return queryset
        if value:
            return queryset.filter(workflow_status__status='published')
        return queryset.exclude(workflow_status__status='published')
    
    def filter_is_scheduled(self, queryset, name, value):
        """Pages avec publication programmée"""
        if not HAS_WORKFLOW:
            return queryset
        if value:
            return queryset.filter(
                workflow_status__status='scheduled',
                scheduling__scheduled_publish_date__isnull=False
            )
        return queryset.exclude(workflow_status__status='scheduled')
    
    # === HIERARCHY METHODS ===
    
    def filter_hierarchy_level(self, queryset, name, value):
        """Niveau hiérarchique (1-3) - VRAIS relations"""
        if value == 1:
            return queryset.filter(hierarchy__parent__isnull=True)
        elif value == 2:
            return queryset.filter(
                hierarchy__parent__isnull=False,
                hierarchy__parent__hierarchy__parent__isnull=True
            )
        elif value == 3:
            return queryset.filter(
                hierarchy__parent__isnull=False,
                hierarchy__parent__hierarchy__parent__isnull=False
            )
        return queryset
    
    def filter_has_parent(self, queryset, name, value):
        """Pages avec/sans parent - VRAI related_name"""
        if value:
            return queryset.filter(hierarchy__parent__isnull=False)
        return queryset.filter(hierarchy__parent__isnull=True)
    
    def filter_has_children(self, queryset, name, value):
        """Pages avec/sans enfants - VRAI related_name"""
        if value:
            return queryset.filter(children_hierarchy__isnull=False).distinct()
        return queryset.filter(children_hierarchy__isnull=True)
    
    def filter_is_root_page(self, queryset, name, value):
        """Pages racines uniquement"""
        if value:
            return queryset.filter(hierarchy__parent__isnull=True)
        return queryset.filter(hierarchy__parent__isnull=False)
    
    # === KEYWORDS METHODS ===
    
    def filter_has_keywords(self, queryset, name, value):
        """Pages avec/sans mots-clés - VRAI related_name"""
        if not HAS_KEYWORDS:
            return queryset
        if value:
            return queryset.filter(page_keywords__isnull=False).distinct()
        return queryset.filter(page_keywords__isnull=True)
    
    def filter_keywords_count(self, queryset, name, value):
        """Nombre de mots-clés - VRAI related_name"""
        if not HAS_KEYWORDS:
            return queryset
        
        queryset = queryset.annotate(
            keywords_count=Count('page_keywords', distinct=True)
        )
        
        if value.start is not None:
            queryset = queryset.filter(keywords_count__gte=value.start)
        if value.stop is not None:
            queryset = queryset.filter(keywords_count__lte=value.stop)
        
        return queryset
    
    def filter_has_primary_keyword(self, queryset, name, value):
        """Pages avec mot-clé principal - VRAI related_name + choices"""
        if not HAS_KEYWORDS:
            return queryset
        if value:
            return queryset.filter(page_keywords__keyword_type='primary').distinct()
        return queryset.exclude(page_keywords__keyword_type='primary')
    
    # === SEO METHODS ===
    
    def filter_has_featured_image(self, queryset, name, value):
        """Pages avec/sans image featured - VRAI related_name + field"""
        if value:
            return queryset.exclude(
                Q(seo_config__featured_image__isnull=True) |
                Q(seo_config__featured_image='')
            )
        return queryset.filter(
            Q(seo_config__featured_image__isnull=True) |
            Q(seo_config__featured_image='')
        )
    
    # === LAYOUT METHODS ===
    
    def filter_has_layout(self, queryset, name, value):
        """Pages avec/sans layout configuré - VRAI related_name"""
        if value:
            return queryset.filter(layout_config__isnull=False)
        return queryset.filter(layout_config__isnull=True)
    
    def filter_has_sections(self, queryset, name, value):
        """Pages avec/sans sections - VRAI related_name"""
        if value:
            return queryset.filter(sections__isnull=False).distinct()
        return queryset.filter(sections__isnull=True)
    
    def filter_sections_count(self, queryset, name, value):
        """Nombre de sections - VRAI related_name"""
        queryset = queryset.annotate(
            sections_count=Count('sections', distinct=True)
        )
        
        if value.start is not None:
            queryset = queryset.filter(sections_count__gte=value.start)
        if value.stop is not None:
            queryset = queryset.filter(sections_count__lte=value.stop)
        
        return queryset
    
    # === PERFORMANCE METHODS ===
    
    def filter_needs_regeneration(self, queryset, name, value):
        """Pages nécessitant régénération - VRAI related_name"""
        if value:
            return queryset.filter(
                Q(performance__last_rendered_at__isnull=True) |
                Q(performance__last_rendered_at__lt=models.F('updated_at'))
            )
        return queryset.filter(
            performance__last_rendered_at__isnull=False,
            performance__last_rendered_at__gte=models.F('updated_at')
        )
    
    # === RECHERCHE GLOBALE ===
    
    def filter_search(self, queryset, name, value):
        """Recherche dans titre, URL, meta description"""
        return queryset.filter(
            Q(title__icontains=value) |
            Q(url_path__icontains=value) |
            Q(meta_description__icontains=value)
        )
        
    # ===== WEBSITE CORE FILTERS =====
    website_name = django_filters.CharFilter(
        field_name='website__name',
        lookup_expr='icontains'
    )
    website_url = django_filters.CharFilter(
        field_name='website__url',
        lookup_expr='icontains'
    )
    website_domain_authority = django_filters.RangeFilter(
        field_name='website__domain_authority'
    )
    website_max_competitor_kd = django_filters.RangeFilter(
        field_name='website__max_competitor_kd'
    )
    website_max_competitor_backlinks = django_filters.RangeFilter(
        field_name='website__max_competitor_backlinks'
    )
    
    # ===== WEBSITE CATEGORIZATION FILTERS (🔥 BANGER ZONE) =====
    website_category = django_filters.ModelChoiceFilter(
        field_name='website__categorizations__category',
        queryset=None,  # Défini dans __init__
    )
    website_primary_category = django_filters.ModelChoiceFilter(
        field_name='website__categorizations__category',
        queryset=None,  # Défini dans __init__
        method='filter_primary_category'
    )
    website_category_level = django_filters.NumberFilter(
        method='filter_category_level'
    )
    categorization_source = django_filters.ChoiceFilter(
        field_name='website__categorizations__source',
        choices=[
            ('manual', 'Manuelle'),
            ('automatic', 'Automatique'), 
            ('ai_suggested', 'Suggérée par IA'),
            ('imported', 'Importée'),
        ]
    )
    has_primary_category = django_filters.BooleanFilter(
        method='filter_has_primary_category'
    )
    
    # ===== MÉTRIQUES CATÉGORIE vs SITE =====
    da_above_category_typical = django_filters.BooleanFilter(
        method='filter_da_above_typical'
    )
    pages_count_above_typical = django_filters.BooleanFilter(
        method='filter_pages_above_typical'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Import dynamique pour éviter circular imports
        try:
            from seo_websites_categorization.models import WebsiteCategory
            self.filters['website_category'].queryset = WebsiteCategory.objects.all()
            self.filters['website_primary_category'].queryset = WebsiteCategory.objects.all()
        except ImportError:
            pass

    # ===== MÉTHODES CATÉGORISATION =====
    
    def filter_primary_category(self, queryset, name, value):
        """Pages de sites avec cette catégorie PRINCIPALE"""
        return queryset.filter(
            website__categorizations__category=value,
            website__categorizations__is_primary=True
        ).distinct()
    
    def filter_category_level(self, queryset, name, value):
        """Pages de sites selon niveau de catégorie (0=racine, 1=sous-cat)"""
        try:
            from seo_websites_categorization.models import WebsiteCategory
            categories_at_level = WebsiteCategory.objects.filter(
                parent__isnull=(value == 0)
            )
            if value > 0:
                # Pour niveau > 0, filtrer récursivement
                pass  # Logique complexe si besoin
            
            return queryset.filter(
                website__categorizations__category__in=categories_at_level
            ).distinct()
        except ImportError:
            return queryset
    
    def filter_has_primary_category(self, queryset, name, value):
        """Pages de sites avec/sans catégorie principale"""
        if value:
            return queryset.filter(
                website__categorizations__is_primary=True
            ).distinct()
        return queryset.exclude(
            website__categorizations__is_primary=True
        )
    
    def filter_da_above_typical(self, queryset, name, value):
        """Sites avec DA supérieur au typique de leur catégorie"""
        if not value:
            return queryset
        
        try:
            from django.db.models import F
            return queryset.filter(
                website__domain_authority__gt=F(
                    'website__categorizations__category__typical_da_range_max'
                ),
                website__categorizations__is_primary=True
            ).distinct()
        except ImportError:
            return queryset
    
    def filter_pages_above_typical(self, queryset, name, value):
        """Sites avec plus de pages que le typique de leur catégorie"""
        if not value:
            return queryset
        
        try:
            from django.db.models import F, Count
            return queryset.annotate(
                pages_count=Count('website__pages', distinct=True)
            ).filter(
                pages_count__gt=F(
                    'website__categorizations__category__typical_pages_count'
                ),
                website__categorizations__is_primary=True
            ).distinct()
        except ImportError:
            return queryset    
        
        
        
    # ===== WEBSITE DESIGN FILTERS =====

    # Config couleurs du site
    website_has_color_config = django_filters.BooleanFilter(
        method='filter_website_has_color_config'
    )
    website_primary_color = django_filters.CharFilter(
        method='filter_website_primary_color'
    )

    # Config typo du site
    website_has_typography_config = django_filters.BooleanFilter(
        method='filter_website_has_typography_config'
    )
    website_font_primary = django_filters.CharFilter(
        method='filter_website_font_primary'
    )
    website_base_font_size = django_filters.RangeFilter(
        method='filter_website_base_font_size'
    )

    # Config layout du site
    website_has_layout_config = django_filters.BooleanFilter(
        method='filter_website_has_layout_config'
    )
    website_max_width = django_filters.CharFilter(
        field_name='website__layout_config__max_width_override'
    )
    website_nav_breakpoint = django_filters.ChoiceFilter(
        field_name='website__layout_config__nav_collapse_breakpoint',
        choices=[('sm', 'Small'), ('md', 'Medium'), ('lg', 'Large')]
    )

    # Config Tailwind du site
    website_has_tailwind = django_filters.BooleanFilter(
        method='filter_website_has_tailwind'
    )
    website_tailwind_outdated = django_filters.BooleanFilter(
        method='filter_website_tailwind_outdated'
    )

    # Design system completeness pour pages
    pages_design_ready = django_filters.BooleanFilter(
        method='filter_pages_design_ready'
    )
        
        
    # ===== WEBSITE DESIGN METHODS =====

    def filter_website_has_color_config(self, queryset, name, value):
        """Pages de sites avec/sans config couleurs"""
        if value:
            return queryset.filter(website__color_config__isnull=False)
        return queryset.filter(website__color_config__isnull=True)

    def filter_website_primary_color(self, queryset, name, value):
        """Pages de sites avec couleur primaire spécifique"""
        return queryset.filter(
            Q(website__color_config__primary_override=value) |
            Q(website__brand__color_palette__primary_color=value,
            website__color_config__primary_override__isnull=True)
        )

    def filter_website_has_typography_config(self, queryset, name, value):
        """Pages de sites avec/sans config typo"""
        if value:
            return queryset.filter(website__typography_config__isnull=False)
        return queryset.filter(website__typography_config__isnull=True)

    def filter_website_font_primary(self, queryset, name, value):
        """Pages de sites avec font primaire spécifique"""
        return queryset.filter(
            Q(website__typography_config__font_primary_override__icontains=value) |
            Q(website__brand__typography__font_primary__icontains=value,
            website__typography_config__font_primary_override__isnull=True)
        )

    def filter_website_base_font_size(self, queryset, name, value):
        """Pages de sites avec taille de base dans range"""
        # Logique pour combiner override + brand default
        queryset = queryset.annotate(
            effective_font_size=models.Case(
                models.When(
                    website__typography_config__base_font_size_override__isnull=False,
                    then=F('website__typography_config__base_font_size_override')
                ),
                default=F('website__brand__typography__base_font_size'),
                output_field=models.IntegerField()
            )
        )
        
        if value.start is not None:
            queryset = queryset.filter(effective_font_size__gte=value.start)
        if value.stop is not None:
            queryset = queryset.filter(effective_font_size__lte=value.stop)
        
        return queryset

    def filter_website_has_layout_config(self, queryset, name, value):
        """Pages de sites avec/sans config layout"""
        if value:
            return queryset.filter(website__layout_config__isnull=False)
        return queryset.filter(website__layout_config__isnull=True)

    def filter_website_has_tailwind(self, queryset, name, value):
        """Pages de sites avec/sans config Tailwind"""
        if value:
            return queryset.filter(website__tailwind_config__isnull=False)
        return queryset.filter(website__tailwind_config__isnull=True)

    def filter_website_tailwind_outdated(self, queryset, name, value):
        """Pages de sites avec Tailwind à régénérer"""
        if value:
            return queryset.filter(
                Q(website__tailwind_config__last_generated_at__isnull=True) |
                Q(website__tailwind_config__last_generated_at__lt=F('website__updated_at'))
            )
        return queryset.filter(
            website__tailwind_config__last_generated_at__isnull=False,
            website__tailwind_config__last_generated_at__gte=F('website__updated_at')
        )

    def filter_pages_design_ready(self, queryset, name, value):
        """Pages de sites avec design system complet"""
        if value:
            return queryset.filter(
                website__color_config__isnull=False,
                website__typography_config__isnull=False,
                website__layout_config__isnull=False,
                website__tailwind_config__isnull=False
            )
        return queryset.exclude(
            website__color_config__isnull=False,
            website__typography_config__isnull=False,
            website__layout_config__isnull=False,
            website__tailwind_config__isnull=False
        )
    