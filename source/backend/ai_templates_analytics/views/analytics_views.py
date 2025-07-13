# backend/ai_templates_analytics/views/analytics_views.py

from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg, Sum, Count
from common.views.mixins import BrandScopedViewSetMixin, AnalyticsViewSetMixin
from common.permissions.business_permissions import IsAuthenticated, IsBrandMember
from ..models import TemplateUsageMetrics, TemplatePerformance, TemplatePopularity, TemplateFeedback
from ..serializers import (
    TemplateUsageMetricsSerializer, TemplatePerformanceSerializer,
    TemplatePopularitySerializer, TemplateFeedbackSerializer
)
from ..filters import TemplatePerformanceFilter, TemplateFeedbackFilter

class TemplateUsageMetricsViewSet(BrandScopedViewSetMixin, ReadOnlyModelViewSet):
    """Métriques d'usage des templates"""
    queryset = TemplateUsageMetrics.objects.select_related('template')
    serializer_class = TemplateUsageMetricsSerializer
    permission_classes = [IsAuthenticated, IsBrandMember]
    ordering = ['-popularity_score', '-total_uses']
    brand_field = 'template__brand'
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Dashboard métriques globales"""
        queryset = self.filter_queryset(self.get_queryset())
        
        dashboard_data = {
            'total_templates': queryset.count(),
            'total_uses': queryset.aggregate(Sum('total_uses'))['total_uses__sum'] or 0,
            'avg_success_rate': queryset.aggregate(
                avg_success=Avg('successful_generations')
            )['avg_success'] or 0,
            'most_popular': TemplateUsageMetricsSerializer(
                queryset.first()
            ).data if queryset.exists() else None
        }
        
        return Response(dashboard_data)

class TemplatePerformanceViewSet(BrandScopedViewSetMixin, ModelViewSet):
    """Performance détaillée des templates"""
    queryset = TemplatePerformance.objects.select_related('template', 'user')
    serializer_class = TemplatePerformanceSerializer
    permission_classes = [IsAuthenticated, IsBrandMember]
    filterset_class = TemplatePerformanceFilter
    ordering = ['-created_at']
    brand_field = 'template__brand'
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TemplatePopularityViewSet(BrandScopedViewSetMixin, ReadOnlyModelViewSet):
    """Classements de popularité"""
    queryset = TemplatePopularity.objects.select_related('template', 'category', 'brand')
    serializer_class = TemplatePopularitySerializer
    permission_classes = [IsAuthenticated, IsBrandMember]
    ordering = ['ranking_period', 'rank_position']
    brand_field = 'brand'
    
    @action(detail=False, methods=['get'])
    def current_rankings(self, request):
        """Classements actuels par période"""
        rankings = {}
        periods = ['daily', 'weekly', 'monthly']
        
        for period in periods:
            latest_rankings = self.get_queryset().filter(
                ranking_period=period
            ).order_by('rank_position')[:10]
            
            rankings[period] = TemplatePopularitySerializer(
                latest_rankings, many=True
            ).data
        
        return Response(rankings)

class TemplateFeedbackViewSet(BrandScopedViewSetMixin, ModelViewSet):
    """Feedback utilisateurs"""
    queryset = TemplateFeedback.objects.select_related('template', 'user')
    serializer_class = TemplateFeedbackSerializer
    permission_classes = [IsAuthenticated, IsBrandMember]
    filterset_class = TemplateFeedbackFilter
    ordering = ['-created_at']
    brand_field = 'template__brand'
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def ratings_summary(self, request):
        """Résumé des notes par template"""
        queryset = self.filter_queryset(self.get_queryset())
        
        summary = queryset.values('template__name').annotate(
            avg_rating=Avg('rating'),
            total_reviews=Count('id')
        ).order_by('-avg_rating')
        
        return Response(summary)
