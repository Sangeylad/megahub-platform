# backend/ai_templates_workflow/serializers/workflow_serializers.py

from rest_framework import serializers
from common.serializers.mixins import DynamicFieldsSerializer
from ..models import TemplateValidationRule, TemplateValidationResult, TemplateApproval, TemplateReview

class TemplateValidationRuleSerializer(DynamicFieldsSerializer):
    """Serializer pour règles de validation"""
    
    class Meta:
        model = TemplateValidationRule
        fields = [
            'id', 'name', 'description', 'rule_type', 'validation_function',
            'is_active', 'is_blocking', 'error_message', 'created_at'
        ]

class TemplateValidationResultSerializer(DynamicFieldsSerializer):
    """Serializer pour résultats de validation"""
    template_name = serializers.CharField(source='template.name', read_only=True)
    rule_name = serializers.CharField(source='validation_rule.name', read_only=True)
    validated_by_username = serializers.CharField(source='validated_by.username', read_only=True)
    
    class Meta:
        model = TemplateValidationResult
        fields = [
            'id', 'template', 'template_name', 'validation_rule', 'rule_name',
            'is_valid', 'error_details', 'validated_by', 'validated_by_username',
            'validation_data', 'created_at'
        ]
        read_only_fields = ['validated_by']

class TemplateApprovalSerializer(DynamicFieldsSerializer):
    """Serializer pour approbations de templates"""
    template_name = serializers.CharField(source='template.name', read_only=True)
    submitted_by_username = serializers.CharField(source='submitted_by.username', read_only=True)
    reviewed_by_username = serializers.CharField(source='reviewed_by.username', read_only=True)
    reviews_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TemplateApproval
        fields = [
            'id', 'template', 'template_name', 'status', 'submitted_by', 'submitted_by_username',
            'reviewed_by', 'reviewed_by_username', 'submitted_at', 'reviewed_at',
            'rejection_reason', 'reviews_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['submitted_by', 'reviewed_by']
    
    def get_reviews_count(self, obj):
        return obj.reviews.count()

class TemplateReviewSerializer(DynamicFieldsSerializer):
    """Serializer pour reviews de templates"""
    approval_template_name = serializers.CharField(source='approval.template.name', read_only=True)
    reviewer_username = serializers.CharField(source='reviewer.username', read_only=True)
    
    class Meta:
        model = TemplateReview
        fields = [
            'id', 'approval', 'approval_template_name', 'reviewer', 'reviewer_username',
            'comment', 'rating', 'review_type', 'created_at'
        ]
        read_only_fields = ['reviewer']
