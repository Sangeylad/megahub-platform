# seo_pages_layout - Page Layout Models

## PageLayout

**Champs:**
- `page` : OneToOneField('seo_pages_content.Page')
- `render_strategy` : CharField(max_length=20, choices, default='sections')
- `layout_data` : JSONField(default=dict)

**Choices:**

### RENDER_STRATEGY_CHOICES
- `sections` : Page Builder Sections
- `markdown` : Markdown Content
- `custom` : Custom Template

**Relations:**
- `page` → seo_pages_content.Page (CASCADE)

**Contraintes:**
- OneToOne avec Page

---

## PageSection

**Champs:**
- `page` : ForeignKey('seo_pages_content.Page')
- `parent_section` : ForeignKey('self', null=True, blank=True)
- `section_type` : CharField(max_length=50, choices)
- `data` : JSONField(default=dict, blank=True)
- `layout_config` : JSONField(default=dict, blank=True)
- `order` : PositiveIntegerField(default=0)
- `is_active` : BooleanField(default=True)
- `version` : CharField(max_length=10, default='1.0')
- `created_by` : ForeignKey('business.CustomUser', null=True, blank=True)

**Choices:**

### SECTION_TYPE_CHOICES
- `layout_columns` : Layout en Colonnes
- `layout_grid` : Layout en Grille
- `layout_stack` : Layout Vertical
- `hero_banner` : Hero Banner
- `cta_banner` : CTA Banner
- `features_grid` : Features Grid
- `rich_text` : Rich Text Block

**Relations:**
- `page` → seo_pages_content.Page (CASCADE)
- `parent_section` → self (CASCADE)
- `created_by` → business.CustomUser (SET_NULL)

**Contraintes:**
- unique_together: ('page', 'parent_section', 'order')
- Validation : Hiérarchie limitée à 2 niveaux maximum
- Validation : Section parent doit être sur la même page