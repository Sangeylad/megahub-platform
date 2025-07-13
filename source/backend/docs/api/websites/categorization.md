# seo_websites_categorization - Website Categorization Models

## WebsiteCategory

**Champs:**
- `name` : CharField(max_length=100, unique=True)
- `slug` : SlugField(max_length=120, unique=True, blank=True)
- `description` : TextField(blank=True)
- `color` : CharField(max_length=7, default='#6366f1')
- `parent` : ForeignKey('self', null=True, blank=True)
- `typical_da_range_min` : IntegerField(null=True, blank=True)
- `typical_da_range_max` : IntegerField(null=True, blank=True)
- `typical_pages_count` : IntegerField(null=True, blank=True)
- `display_order` : PositiveIntegerField(default=0)

**Relations:**
- `parent` → self (CASCADE)

**Contraintes:**
- Unique : name, slug

**Choices:**
Aucun

---

## WebsiteCategorization

**Champs:**
- `website` : ForeignKey('seo_websites_core.Website')
- `category` : ForeignKey(WebsiteCategory)
- `is_primary` : BooleanField(default=False)
- `confidence_score` : FloatField(null=True, blank=True)
- `categorized_by` : ForeignKey('business.CustomUser', null=True, blank=True)
- `source` : CharField(max_length=20, choices, default='manual')
- `notes` : TextField(blank=True)

**Choices:**

### CATEGORIZATION_SOURCE_CHOICES
- `manual` : Manuelle
- `automatic` : Automatique
- `ai_suggested` : Suggérée par IA
- `imported` : Importée

**Relations:**
- `website` → seo_websites_core.Website (CASCADE)
- `category` → WebsiteCategory (CASCADE)
- `categorized_by` → business.CustomUser (SET_NULL)

**Contraintes:**
- unique_together: ('website', 'category')