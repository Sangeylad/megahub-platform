# backend/ai_templates_workflow/filters/workflow_filters.py
import django_filters
from ..models import TemplateApproval, TemplateValidationResult

class TemplateApprovalFilter(django_filters.FilterSet):
    status = django_filters.CharFilter()
    template = django_filters.NumberFilter()
    submitted_by = django_filters.NumberFilter()
    
    class Meta:
        model = TemplateApproval
        fields = ['status', 'template', 'submitted_by']

class TemplateValidationResultFilter(django_filters.FilterSet):
    is_valid = django_filters.BooleanFilter()
    validation_rule = django_filters.NumberFilter()
    template = django_filters.NumberFilter()
    
    class Meta:
        model = TemplateValidationResult
        fields = ['is_valid', 'validation_rule', 'template']
