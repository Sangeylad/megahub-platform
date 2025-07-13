# backend/seo_websites_ai_templates_content/models/seo_template_models.py

from django.db import models
from common.models.mixins import TimestampedMixin

class SEOWebsiteTemplate(TimestampedMixin):
    """Templates spécialisés pour génération contenu SEO"""
    base_template = models.OneToOneField('ai_templates_core.BaseTemplate', on_delete=models.CASCADE, related_name='seo_config')
    category = models.ForeignKey('ai_templates_categories.TemplateCategory', on_delete=models.SET_NULL, null=True, blank=True)
    page_type = models.CharField(max_length=50, choices=[
        ('landing', 'Landing Page'),
        ('vitrine', 'Page Vitrine'),
        ('service', 'Page Service'),
        ('produit', 'Page Produit'),
        ('blog', 'Article Blog'),
        ('category', 'Page Catégorie')
    ])
    search_intent = models.CharField(max_length=20, choices=[
        ('TOFU', 'Top of Funnel'),
        ('MOFU', 'Middle of Funnel'),
        ('BOFU', 'Bottom of Funnel'),
        ('BRAND', 'Brand')
    ], default='TOFU')
    target_word_count = models.PositiveIntegerField(default=800, help_text="Nombre de mots cible")
    keyword_density_target = models.FloatField(default=1.5, help_text="Densité mots-clés cible (%)")
    
    class Meta:
        db_table = 'seo_website_template'
        indexes = [
            models.Index(fields=['page_type', 'search_intent']),
            models.Index(fields=['category'])
        ]
    
    def __str__(self):
        return f"SEO: {self.base_template.name} ({self.page_type})"

class SEOTemplateConfig(TimestampedMixin):
    """Configuration SEO avancée pour templates"""
    seo_template = models.OneToOneField(SEOWebsiteTemplate, on_delete=models.CASCADE, related_name='advanced_config')
    h1_structure = models.CharField(max_length=200, default="{{target_keyword}} - {{brand_name}}")
    h2_pattern = models.TextField(default="## {{secondary_keyword}}\n\n{{content_section}}")
    meta_title_template = models.CharField(max_length=200, default="{{target_keyword}} | {{brand_name}}")
    meta_description_template = models.TextField(default="{{description_intro}} {{target_keyword}} {{brand_name}}. {{cta_phrase}}")
    internal_linking_rules = models.JSONField(default=dict, help_text="Règles de maillage interne")
    schema_markup_type = models.CharField(max_length=50, blank=True, help_text="Type de schema.org")
    
    class Meta:
        db_table = 'seo_template_config'
    
    def __str__(self):
        return f"Config SEO: {self.seo_template.base_template.name}"

class KeywordIntegrationRule(TimestampedMixin):
    """Règles d'intégration automatique des mots-clés"""
    seo_template = models.ForeignKey(SEOWebsiteTemplate, on_delete=models.CASCADE, related_name='keyword_rules')
    keyword_type = models.CharField(max_length=20, choices=[
        ('primary', 'Principal'),
        ('secondary', 'Secondaire'),
        ('anchor', 'Ancre'),
        ('semantic', 'Sémantique')
    ])
    placement_rules = models.JSONField(default=dict, help_text="Règles de placement (H1, H2, paragraphes)")
    density_min = models.FloatField(default=0.5, help_text="Densité minimum (%)")
    density_max = models.FloatField(default=3.0, help_text="Densité maximum (%)")
    natural_variations = models.BooleanField(default=True, help_text="Utiliser variations naturelles")
    
    class Meta:
        db_table = 'keyword_integration_rule'
        unique_together = ['seo_template', 'keyword_type']
    
    def __str__(self):
        return f"{self.seo_template.base_template.name} - {self.keyword_type}"

class PageTypeTemplate(TimestampedMixin):
    """Templates prédéfinis par type de page"""
    name = models.CharField(max_length=100)
    page_type = models.CharField(max_length=50)
    template_structure = models.TextField(help_text="Structure template avec sections")
    default_sections = models.JSONField(default=list, help_text="Sections par défaut")
    required_variables = models.JSONField(default=list, help_text="Variables obligatoires")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'page_type_template'
        unique_together = ['name', 'page_type']
    
    def __str__(self):
        return f"{self.name} ({self.page_type})"
