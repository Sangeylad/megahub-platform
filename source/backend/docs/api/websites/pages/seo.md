# seo_pages_seo - Page SEO Models

## PagePerformance

**Champs:**
- `page` : OneToOneField('seo_pages_content.Page')
- `last_rendered_at` : DateTimeField(null=True, blank=True)
- `render_time_ms` : PositiveIntegerField(null=True, blank=True)
- `cache_hits` : PositiveIntegerField(default=0)
- `last_crawled_at` : DateTimeField(null=True, blank=True)

**Relations:**
- `page` → seo_pages_content.Page (CASCADE)

**Contraintes:**
- OneToOne avec Page

**Choices:**
Aucun

---

## PageSEO

**Champs:**
- `page` : OneToOneField('seo_pages_content.Page')
- `featured_image` : URLField(blank=True, null=True)
- `sitemap_priority` : DecimalField(max_digits=2, decimal_places=1, default=0.5)
- `sitemap_changefreq` : CharField(max_length=20, choices, default='weekly')
- `exclude_from_sitemap` : BooleanField(default=False)

**Choices:**

### CHANGEFREQ_CHOICES
- `always` : Always
- `hourly` : Hourly
- `daily` : Daily
- `weekly` : Weekly
- `monthly` : Monthly
- `yearly` : Yearly
- `never` : Never

**Relations:**
- `page` → seo_pages_content.Page (CASCADE)

**Contraintes:**
- OneToOne avec Page