# backend/ai_templates_core/admin/template_admin.py

from django.contrib import admin
from ..models import TemplateType, BrandTemplateConfig, BaseTemplate

@admin.register(TemplateType)
class TemplateTypeAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'name', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'display_name']

@admin.register(BrandTemplateConfig)
class BrandTemplateConfigAdmin(admin.ModelAdmin):
    list_display = ['brand', 'max_templates_per_type', 'allow_custom_templates', 'created_at']
    list_filter = ['allow_custom_templates']
    search_fields = ['brand__name']

@admin.register(BaseTemplate)
class BaseTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'template_type', 'brand', 'is_active', 'is_public', 'created_by', 'created_at']
    list_filter = ['template_type', 'is_active', 'is_public', 'created_at']
    search_fields = ['name', 'brand__name']
    readonly_fields = ['created_by']
    
    def save_model(self, request, obj, form, change):
        if not change:  # Création
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
