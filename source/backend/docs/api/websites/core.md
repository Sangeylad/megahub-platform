# seo_websites_core - Website Core Models

## Website

**Champs:**
- `name` : CharField(max_length=255)
- `url` : URLField()
- `brand` : OneToOneField('business.Brand')
- `domain_authority` : IntegerField(null=True, blank=True)
- `max_competitor_backlinks` : IntegerField(null=True, blank=True)
- `max_competitor_kd` : FloatField(null=True, blank=True)

**Relations:**
- `brand` → business.Brand (CASCADE)

**Contraintes:**
- OneToOne avec Brand

**Choices:**
Aucun