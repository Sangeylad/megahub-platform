# backend/ai_templates_categories/admin/category_admin.py
from django.contrib import admin
from ..models import TemplateCategory, TemplateTag, CategoryPermission

@admin.register(TemplateCategory)
class TemplateCategoryAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'parent', 'level', 'sort_order', 'is_active']
    list_filter = ['level', 'is_active', 'parent']
    search_fields = ['name', 'display_name']

@admin.register(TemplateTag)
class TemplateTagAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'color', 'usage_count', 'is_active']
    list_filter = ['color', 'is_active']
    search_fields = ['name', 'display_name']

@admin.register(CategoryPermission)
class CategoryPermissionAdmin(admin.ModelAdmin):
    list_display = ['category', 'permission_type', 'required_plan', 'is_active']
    list_filter = ['permission_type', 'required_plan', 'is_active']
