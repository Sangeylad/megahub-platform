# seo_pages_content - Page Models

## Page

**Champs:**
- `title` : CharField(max_length=255)
- `url_path` : CharField(max_length=500, blank=True)
- `meta_description` : TextField(blank=True, null=True)
- `website` : ForeignKey('seo_websites_core.Website')
- `search_intent` : CharField(max_length=10, choices, null=True, blank=True)
- `page_type` : CharField(max_length=20, choices, default='vitrine')

**Choices:**

### SEARCH_INTENT_CHOICES
- `TOFU` : Top of Funnel
- `MOFU` : Middle of Funnel
- `BOFU` : Bottom of Funnel

### PAGE_TYPE_CHOICES
- `vitrine` : Vitrine
- `blog` : Blog
- `blog_category` : Catégorie Blog
- `produit` : Produit/Service
- `landing` : Landing Page
- `categorie` : Page Catégorie
- `legal` : Page Légale
- `outils` : Outils
- `autre` : Autre

**Relations:**
- `website` → seo_websites_core.Website (CASCADE)

**Contraintes:**
- unique_together: ('website', 'url_path')