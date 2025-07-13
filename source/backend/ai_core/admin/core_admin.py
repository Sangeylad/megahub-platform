# backend/ai_core/admin/core_admin.py

from django.contrib import admin
from ..models import AIJob, AIJobType

@admin.register(AIJobType)
class AIJobTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'estimated_duration_seconds', 'requires_async']
    list_filter = ['category', 'requires_async']
    search_fields = ['name', 'description']

@admin.register(AIJob)
class AIJobAdmin(admin.ModelAdmin):
    list_display = ['job_id', 'job_type', 'status', 'brand', 'created_by', 'created_at']
    list_filter = ['status', 'job_type', 'priority', 'is_async']
    search_fields = ['job_id', 'description']
    readonly_fields = ['job_id', 'created_at', 'updated_at']
