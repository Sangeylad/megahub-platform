# backend/ai_templates_storage/admin/storage_admin.py

from django.contrib import admin
from ..models import TemplateVariable, TemplateVersion

@admin.register(TemplateVariable)
class TemplateVariableAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_name', 'variable_type', 'is_required', 'created_at']
    list_filter = ['variable_type', 'is_required']
    search_fields = ['name', 'display_name']

@admin.register(TemplateVersion)
class TemplateVersionAdmin(admin.ModelAdmin):
    list_display = ['template', 'version_number', 'is_current', 'created_by', 'created_at']
    list_filter = ['is_current', 'created_at']
    search_fields = ['template__name']
    readonly_fields = ['version_number', 'created_by']
    
    def save_model(self, request, obj, form, change):
        if not change:  # Création
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
