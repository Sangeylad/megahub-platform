# backend/ai_templates_workflow/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TemplateValidationRuleViewSet, TemplateValidationResultViewSet,
    TemplateApprovalViewSet, TemplateReviewViewSet
)

router = DefaultRouter()
router.register(r'validation-rules', TemplateValidationRuleViewSet, basename='templatevalidationrule')
router.register(r'validation-results', TemplateValidationResultViewSet, basename='templatevalidationresult')
router.register(r'approvals', TemplateApprovalViewSet, basename='templateapproval')
router.register(r'reviews', TemplateReviewViewSet, basename='templatereview')

urlpatterns = [
    path('', include(router.urls)),
]
