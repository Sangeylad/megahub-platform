# backend/ai_templates_analytics/admin/analytics_admin.py
from django.contrib import admin
from ..models import TemplateUsageMetrics, TemplatePerformance, TemplatePopularity, TemplateFeedback

@admin.register(TemplateUsageMetrics)
class TemplateUsageMetricsAdmin(admin.ModelAdmin):
    list_display = ['template', 'total_uses', 'success_rate', 'popularity_score']
    readonly_fields = ['success_rate']

@admin.register(TemplatePerformance)
class TemplatePerformanceAdmin(admin.ModelAdmin):
    list_display = ['template', 'user', 'generation_time', 'was_successful', 'created_at']
    list_filter = ['was_successful', 'created_at']

@admin.register(TemplatePopularity)
class TemplatePopularityAdmin(admin.ModelAdmin):
    list_display = ['template', 'ranking_period', 'rank_position', 'usage_count']
    list_filter = ['ranking_period', 'period_start']

@admin.register(TemplateFeedback)
class TemplateFeedbackAdmin(admin.ModelAdmin):
    list_display = ['template', 'user', 'rating', 'feedback_type', 'is_public']
    list_filter = ['rating', 'feedback_type', 'is_public']
