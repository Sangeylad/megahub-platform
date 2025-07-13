# seo_pages_hierarchy - Page Hierarchy Models

## PageBreadcrumb

**Champs:**
- `page` : OneToOneField('seo_pages_content.Page')
- `breadcrumb_json` : JSONField(default=list)

**Relations:**
- `page` → seo_pages_content.Page (CASCADE)

**Contraintes:**
- OneToOne avec Page

---

## PageHierarchy

**Champs:**
- `page` : OneToOneField('seo_pages_content.Page')
- `parent` : ForeignKey('seo_pages_content.Page', null=True, blank=True)

**Relations:**
- `page` → seo_pages_content.Page (CASCADE)
- `parent` → seo_pages_content.Page (CASCADE)

**Contraintes:**
- OneToOne avec Page
- Validation : 3 niveaux hiérarchiques maximum
- Validation : Page ne peut pas être son propre parent

**Choices:**
Aucun