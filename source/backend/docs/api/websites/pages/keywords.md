# seo_pages_keywords - Page Keywords Models

## PageKeyword

**Champs:**
- `page` : ForeignKey('seo_pages_content.Page')
- `keyword` : ForeignKey('seo_keywords_base.Keyword')
- `position` : IntegerField(null=True, blank=True)
- `keyword_type` : CharField(max_length=20, choices, default='secondary')
- `source_cocoon` : ForeignKey('keyword_research.SemanticCocoon', null=True, blank=True)
- `is_ai_selected` : BooleanField(default=False)
- `notes` : TextField(null=True, blank=True)

**Choices:**

### KEYWORD_TYPE_CHOICES
- `primary` : Primaire
- `secondary` : Secondaire
- `anchor` : Ancre

**Relations:**
- `page` → seo_pages_content.Page (CASCADE)
- `keyword` → seo_keywords_base.Keyword (CASCADE)
- `source_cocoon` → keyword_research.SemanticCocoon (SET_NULL)

**Contraintes:**
- unique_together: ('page', 'keyword')
- Validation : Un seul mot-clé primaire par page
- Validation : Pas de doublon keyword/page