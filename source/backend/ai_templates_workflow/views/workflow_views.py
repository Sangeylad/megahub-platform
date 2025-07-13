# backend/ai_templates_workflow/views/workflow_views.py

from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from common.views.mixins import BrandScopedViewSetMixin, AnalyticsViewSetMixin
from common.permissions.business_permissions import IsAuthenticated, IsBrandMember, IsCompanyAdmin
from ..models import TemplateValidationRule, TemplateValidationResult, TemplateApproval, TemplateReview
from ..serializers import (
    TemplateValidationRuleSerializer, TemplateValidationResultSerializer,
    TemplateApprovalSerializer, TemplateReviewSerializer
)
from ..filters import TemplateApprovalFilter, TemplateValidationResultFilter

class TemplateValidationRuleViewSet(ReadOnlyModelViewSet):
    """Règles de validation - admin seulement"""
    queryset = TemplateValidationRule.objects.filter(is_active=True)
    serializer_class = TemplateValidationRuleSerializer
    permission_classes = [IsAuthenticated, IsCompanyAdmin]
    ordering = ['rule_type', 'name']

class TemplateValidationResultViewSet(BrandScopedViewSetMixin, ReadOnlyModelViewSet):
    """Résultats de validation"""
    queryset = TemplateValidationResult.objects.select_related('template', 'validation_rule', 'validated_by')
    serializer_class = TemplateValidationResultSerializer
    permission_classes = [IsAuthenticated, IsBrandMember]
    filterset_class = TemplateValidationResultFilter
    ordering = ['-created_at']
    brand_field = 'template__brand'

class TemplateApprovalViewSet(BrandScopedViewSetMixin, AnalyticsViewSetMixin, ModelViewSet):
    """Processus d'approbation des templates"""
    queryset = TemplateApproval.objects.select_related('template', 'submitted_by', 'reviewed_by')
    serializer_class = TemplateApprovalSerializer
    permission_classes = [IsAuthenticated, IsBrandMember]
    filterset_class = TemplateApprovalFilter
    ordering = ['-created_at']
    brand_field = 'template__brand'
    
    @action(detail=True, methods=['post'])
    def submit_for_review(self, request, pk=None):
        """Soumettre pour review"""
        approval = self.get_object()
        if approval.status == 'draft':
            approval.status = 'pending_review'
            approval.submitted_by = request.user
            approval.submitted_at = timezone.now()
            approval.save()
            return Response({'status': 'Soumis pour review'})
        return Response({'error': 'Statut invalide'}, status=400)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approuver template"""
        approval = self.get_object()
        if approval.status == 'pending_review':
            approval.status = 'approved'
            approval.reviewed_by = request.user
            approval.reviewed_at = timezone.now()
            approval.save()
            return Response({'status': 'Template approuvé'})
        return Response({'error': 'Statut invalide'}, status=400)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Rejeter template"""
        approval = self.get_object()
        rejection_reason = request.data.get('rejection_reason', '')
        if approval.status == 'pending_review':
            approval.status = 'rejected'
            approval.reviewed_by = request.user
            approval.reviewed_at = timezone.now()
            approval.rejection_reason = rejection_reason
            approval.save()
            return Response({'status': 'Template rejeté'})
        return Response({'error': 'Statut invalide'}, status=400)

class TemplateReviewViewSet(BrandScopedViewSetMixin, ModelViewSet):
    """Reviews et commentaires"""
    queryset = TemplateReview.objects.select_related('approval', 'reviewer')
    serializer_class = TemplateReviewSerializer
    permission_classes = [IsAuthenticated, IsBrandMember]
    ordering = ['-created_at']
    brand_field = 'approval__template__brand'
    
    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)
