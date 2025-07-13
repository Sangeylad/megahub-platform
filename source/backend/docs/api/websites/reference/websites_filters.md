# seo_websites_core - Website Filters

## WebsiteFilter

### Filtres de Base (seo_websites_core)

**Champs de base:**
- `name` : CharFilter(lookup_expr='icontains')
- `url` : CharFilter(lookup_expr='icontains')
- `domain_authority` : RangeFilter()
- `max_competitor_backlinks` : RangeFilter()
- `max_competitor_kd` : RangeFilter()

### Filtres Brand (business)

**Champs brand:**
- `brand_name` : CharFilter(field_name='brand__name', lookup_expr='icontains')
- `brand_company` : NumberFilter(field_name='brand__company')
- `has_chatgpt_key` : BooleanFilter()
- `has_gemini_key` : BooleanFilter()

### Filtres Pages Content (seo_pages_content)

**Champs pages content:**
- `pages_count` : RangeFilter()
- `has_pages` : BooleanFilter()
- `page_types` : CharFilter() (comma-separated)
- `search_intents` : CharFilter() (comma-separated)
- `has_vitrine_pages` : BooleanFilter()
- `has_blog_pages` : BooleanFilter()
- `has_product_pages` : BooleanFilter()

**PAGE_TYPE_CHOICES supportés:**
- `vitrine`, `blog`, `blog_category`, `produit`, `landing`, `categorie`, `legal`, `outils`, `autre`

**SEARCH_INTENT_CHOICES supportés:**
- `TOFU`, `MOFU`, `BOFU`

### Filtres Workflow (seo_pages_workflow)

**Champs workflow:**
- `has_published_pages` : BooleanFilter()
- `has_draft_pages` : BooleanFilter()
- `has_scheduled_pages` : BooleanFilter()
- `published_pages_count` : RangeFilter()
- `publication_ratio` : RangeFilter() (0.0-1.0)

### Filtres Keywords (seo_pages_keywords)

**Champs keywords:**
- `has_keywords` : BooleanFilter()
- `total_keywords_count` : RangeFilter()
- `unique_keywords_count` : RangeFilter()
- `keywords_coverage` : RangeFilter() (0.0-1.0)
- `has_primary_keywords` : BooleanFilter()
- `ai_keywords_ratio` : RangeFilter() (0.0-1.0)
- `avg_keyword_volume` : RangeFilter()

### Filtres SEO (seo_pages_seo)

**Champs SEO:**
- `has_seo_config` : BooleanFilter()
- `has_featured_images` : BooleanFilter()
- `avg_sitemap_priority` : RangeFilter() (0.0-1.0)
- `excluded_from_sitemap_count` : RangeFilter()
- `meta_description_coverage` : RangeFilter() (0.0-1.0)

### Filtres Layout/Page Builder (seo_pages_layout)

**Champs layout:**
- `has_page_builder` : BooleanFilter()
- `sections_count` : RangeFilter()
- `layout_coverage` : RangeFilter() (0.0-1.0)
- `popular_section_types` : CharFilter() (comma-separated)
- `render_strategy` : ChoiceFilter()

**RENDER_STRATEGY_CHOICES:**
- `sections` : Page Builder
- `markdown` : Markdown
- `custom` : Custom Template

**SECTION_TYPE_CHOICES supportés:**
- `layout_columns`, `layout_grid`, `layout_stack`, `hero_banner`, `cta_banner`, `features_grid`, `rich_text`

### Filtres Categorization (seo_websites_categorization)

**Champs categorization:**
- `website_category` : ModelChoiceFilter(field_name='categorizations__category')
- `primary_category` : ModelChoiceFilter()
- `category_level` : NumberFilter() (0=racine, 1+=sous-catégories)
- `categorization_source` : ChoiceFilter(field_name='categorizations__source')
- `has_primary_category` : BooleanFilter()

**CATEGORIZATION_SOURCE_CHOICES:**
- `manual` : Manuelle
- `automatic` : Automatique
- `ai_suggested` : Suggérée par IA
- `imported` : Importée

### Filtres Performance vs Category

**Champs performance vs category:**
- `da_above_category` : BooleanFilter()
- `da_below_category` : BooleanFilter()
- `pages_above_category` : BooleanFilter()
- `pages_below_category` : BooleanFilter()
- `performance_vs_category` : ChoiceFilter()

**PERFORMANCE_VS_CATEGORY_CHOICES:**
- `above` : Au-dessus de la catégorie
- `typical` : Typique de la catégorie
- `below` : En-dessous de la catégorie

### Filtres Sync & OpenAI (seo_websites_core.sync_status)

**Champs sync:**
- `needs_openai_sync` : BooleanFilter()
- `last_synced_after` : DateTimeFilter(field_name='sync_status__last_openai_sync', lookup_expr='gte')
- `sync_version` : NumberFilter(field_name='sync_status__openai_sync_version')

### Recherche Globale

**Champ recherche:**
- `search` : CharFilter() (recherche dans name, url, brand__name)

### Relations Cross-App

**Relations utilisées:**
- `brand` → business.Brand
- `pages` → seo_pages_content.Page
- `pages__workflow_status` → seo_pages_workflow.PageStatus
- `pages__page_keywords` → seo_pages_keywords.PageKeyword
- `pages__seo_config` → seo_pages_seo.PageSEO
- `pages__layout_config` → seo_pages_layout.PageLayout
- `pages__sections` → seo_pages_layout.PageSection
- `categorizations` → seo_websites_categorization.WebsiteCategorization
- `sync_status` → seo_websites_core.WebsiteSyncStatus

### Filtres Calculés Spéciaux

**Ratios et métriques calculées:**
- `publication_ratio` : published_pages / total_pages
- `keywords_coverage` : pages_with_keywords / total_pages
- `ai_keywords_ratio` : ai_selected_keywords / total_keywords
- `layout_coverage` : pages_with_layout / total_pages
- `meta_description_coverage` : pages_with_meta / total_pages

### Types de Valeurs

**BooleanFilter:** true/false
**NumberFilter:** entier
**RangeFilter:** min/max (ex: ?field_min=10&field_max=50)
**CharFilter:** chaîne de caractères (comma-separated pour listes)
**ChoiceFilter:** valeur parmi les choices définies
**DateTimeFilter:** format ISO 8601 (ex: 2024-12-20T14:30:00Z)
**ModelChoiceFilter:** ID de l'objet référencé

### Exemples d'Usage Complexe

```
# Sites avec bonne couverture SEO et keywords
?keywords_coverage_min=0.8&meta_description_coverage_min=0.7&has_primary_keywords=true

# Sites performants vs leur catégorie
?da_above_category=true&pages_above_category=true&has_primary_category=true

# Sites avec page builder moderne
?has_page_builder=true&render_strategy=sections&layout_coverage_min=0.5

# Sites nécessitant attention
?publication_ratio_max=0.5&keywords_coverage_max=0.3&needs_openai_sync=true
```