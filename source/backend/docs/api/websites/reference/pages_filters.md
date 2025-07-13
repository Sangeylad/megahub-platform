# seo_pages_content - Page Filters

## PageFilter

### Filtres de Base (seo_pages_content)

**Champs de base:**
- `title` : CharFilter(lookup_expr='icontains')
- `url_path` : CharFilter(lookup_expr='icontains')
- `website` : NumberFilter()
- `page_type` : ChoiceFilter(choices=Page.PAGE_TYPE_CHOICES)
- `search_intent` : ChoiceFilter(choices=Page.SEARCH_INTENT_CHOICES)
- `has_meta_description` : BooleanFilter()

**Choices disponibles:**

**PAGE_TYPE_CHOICES:**
- `vitrine` : Vitrine
- `blog` : Blog
- `blog_category` : Catégorie Blog
- `produit` : Produit/Service
- `landing` : Landing Page
- `categorie` : Page Catégorie
- `legal` : Page Légale
- `outils` : Outils
- `autre` : Autre

**SEARCH_INTENT_CHOICES:**
- `TOFU` : Top of Funnel
- `MOFU` : Middle of Funnel
- `BOFU` : Bottom of Funnel

### Filtres Workflow (seo_pages_workflow)

**Champs workflow:**
- `workflow_status` : ChoiceFilter(field_name='workflow_status__status')
- `is_published` : BooleanFilter()
- `is_scheduled` : BooleanFilter()
- `status_changed_after` : DateTimeFilter(field_name='workflow_status__status_changed_at', lookup_expr='gte')

### Filtres Hiérarchie (seo_pages_hierarchy)

**Champs hiérarchie:**
- `hierarchy_level` : NumberFilter() (valeurs: 1, 2, 3)
- `has_parent` : BooleanFilter()
- `has_children` : BooleanFilter()
- `is_root_page` : BooleanFilter()

### Filtres Keywords (seo_pages_keywords)

**Champs keywords:**
- `has_keywords` : BooleanFilter()
- `keywords_count` : RangeFilter()
- `has_primary_keyword` : BooleanFilter()
- `keyword_type` : ChoiceFilter(field_name='page_keywords__keyword_type')
- `is_ai_selected` : BooleanFilter(field_name='page_keywords__is_ai_selected')

**KEYWORD_TYPE_CHOICES:**
- `primary` : Primaire
- `secondary` : Secondaire
- `anchor` : Ancre

### Filtres SEO (seo_pages_seo)

**Champs SEO:**
- `sitemap_priority` : RangeFilter(field_name='seo_config__sitemap_priority')
- `sitemap_changefreq` : ChoiceFilter(field_name='seo_config__sitemap_changefreq')
- `has_featured_image` : BooleanFilter()
- `exclude_from_sitemap` : BooleanFilter(field_name='seo_config__exclude_from_sitemap')

**SITEMAP_CHANGEFREQ_CHOICES:**
- `always` : Always
- `hourly` : Hourly
- `daily` : Daily
- `weekly` : Weekly
- `monthly` : Monthly
- `yearly` : Yearly
- `never` : Never

### Filtres Layout (seo_pages_layout)

**Champs layout:**
- `has_layout` : BooleanFilter()
- `render_strategy` : ChoiceFilter(field_name='layout_config__render_strategy')
- `has_sections` : BooleanFilter()
- `sections_count` : RangeFilter()
- `section_type` : CharFilter(field_name='sections__section_type')

**RENDER_STRATEGY_CHOICES:**
- `sections` : Page Builder Sections
- `markdown` : Markdown Content
- `custom` : Custom Template

**SECTION_TYPE_CHOICES:**
- `layout_columns` : Layout en Colonnes
- `layout_grid` : Layout en Grille
- `layout_stack` : Layout Vertical
- `hero_banner` : Hero Banner
- `cta_banner` : CTA Banner
- `features_grid` : Features Grid
- `rich_text` : Rich Text Block

### Filtres Performance (seo_pages_seo)

**Champs performance:**
- `needs_regeneration` : BooleanFilter()
- `last_rendered_after` : DateTimeFilter(field_name='performance__last_rendered_at', lookup_expr='gte')

### Filtres Website Core (seo_websites_core)

**Champs website:**
- `website_name` : CharFilter(field_name='website__name', lookup_expr='icontains')
- `website_url` : CharFilter(field_name='website__url', lookup_expr='icontains')
- `website_domain_authority` : RangeFilter(field_name='website__domain_authority')
- `website_max_competitor_kd` : RangeFilter(field_name='website__max_competitor_kd')
- `website_max_competitor_backlinks` : RangeFilter(field_name='website__max_competitor_backlinks')

### Filtres Website Categorization (seo_websites_categorization)

**Champs categorization:**
- `website_category` : ModelChoiceFilter(field_name='website__categorizations__category')
- `website_primary_category` : ModelChoiceFilter(field_name='website__categorizations__category')
- `website_category_level` : NumberFilter()
- `categorization_source` : ChoiceFilter(field_name='website__categorizations__source')
- `has_primary_category` : BooleanFilter()
- `da_above_category_typical` : BooleanFilter()
- `pages_count_above_typical` : BooleanFilter()

**CATEGORIZATION_SOURCE_CHOICES:**
- `manual` : Manuelle
- `automatic` : Automatique
- `ai_suggested` : Suggérée par IA
- `imported` : Importée

### Recherche Globale

**Champ recherche:**
- `search` : CharFilter() (recherche dans title, url_path, meta_description)

### Relations Cross-App

**Relations utilisées:**
- `workflow_status` → seo_pages_workflow.PageStatus
- `hierarchy` → seo_pages_hierarchy.PageHierarchy
- `page_keywords` → seo_pages_keywords.PageKeyword
- `seo_config` → seo_pages_seo.PageSEO
- `performance` → seo_pages_seo.PagePerformance
- `layout_config` → seo_pages_layout.PageLayout
- `sections` → seo_pages_layout.PageSection
- `website` → seo_websites_core.Website
- `website__categorizations` → seo_websites_categorization.WebsiteCategorization

### Types de Valeurs

**BooleanFilter:** true/false
**NumberFilter:** entier
**RangeFilter:** min/max (ex: ?field_min=10&field_max=50)
**CharFilter:** chaîne de caractères
**ChoiceFilter:** valeur parmi les choices définies
**DateTimeFilter:** format ISO 8601 (ex: 2024-12-20T14:30:00Z)
**ModelChoiceFilter:** ID de l'objet référencé