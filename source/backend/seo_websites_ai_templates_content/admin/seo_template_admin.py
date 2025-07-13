# backend/seo_websites_ai_templates_content/admin/seo_template_admin.py
from django.contrib import admin
from ..models import SEOWebsiteTemplate, SEOTemplateConfig, KeywordIntegrationRule, PageTypeTemplate

@admin.register(SEOWebsiteTemplate)
class SEOWebsiteTemplateAdmin(admin.ModelAdmin):
    list_display = ['base_template', 'page_type', 'search_intent', 'target_word_count']
    list_filter = ['page_type', 'search_intent', 'category']
    search_fields = ['base_template__name']

@admin.register(SEOTemplateConfig)
class SEOTemplateConfigAdmin(admin.ModelAdmin):
    list_display = ['seo_template', 'schema_markup_type']
    search_fields = ['seo_template__base_template__name']

@admin.register(KeywordIntegrationRule)
class KeywordIntegrationRuleAdmin(admin.ModelAdmin):
    list_display = ['seo_template', 'keyword_type', 'density_min', 'density_max']
    list_filter = ['keyword_type']

@admin.register(PageTypeTemplate)
class PageTypeTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'page_type', 'is_active']
    list_filter = ['page_type', 'is_active']
