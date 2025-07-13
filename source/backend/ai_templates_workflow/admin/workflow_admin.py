# backend/ai_templates_workflow/admin/workflow_admin.py
from django.contrib import admin
from ..models import TemplateValidationRule, TemplateValidationResult, TemplateApproval, TemplateReview

@admin.register(TemplateValidationRule)
class TemplateValidationRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'rule_type', 'is_active', 'is_blocking']
    list_filter = ['rule_type', 'is_active', 'is_blocking']

@admin.register(TemplateValidationResult)
class TemplateValidationResultAdmin(admin.ModelAdmin):
    list_display = ['template', 'validation_rule', 'is_valid', 'created_at']
    list_filter = ['is_valid', 'validation_rule']

@admin.register(TemplateApproval)
class TemplateApprovalAdmin(admin.ModelAdmin):
    list_display = ['template', 'status', 'submitted_by', 'reviewed_by', 'created_at']
    list_filter = ['status', 'submitted_at', 'reviewed_at']

@admin.register(TemplateReview)
class TemplateReviewAdmin(admin.ModelAdmin):
    list_display = ['approval', 'reviewer', 'rating', 'review_type', 'created_at']
    list_filter = ['rating', 'review_type']
