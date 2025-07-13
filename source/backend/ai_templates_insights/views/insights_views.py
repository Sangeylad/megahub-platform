# backend/ai_templates_insights/views/insights_views.py

from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from common.views.mixins import BrandScopedViewSetMixin, AnalyticsViewSetMixin
from common.permissions.business_permissions import IsAuthenticated, IsBrandMember
from ..models import TemplateRecommendation, TemplateInsight, OptimizationSuggestion, TrendAnalysis
from ..serializers import (
    TemplateRecommendationSerializer, TemplateInsightSerializer,
    OptimizationSuggestionSerializer, TrendAnalysisSerializer
)
from ..filters import TemplateRecommendationFilter, TemplateInsightFilter

class TemplateRecommendationViewSet(BrandScopedViewSetMixin, ModelViewSet):
    """Recommandations personnalisées"""
    queryset = TemplateRecommendation.objects.select_related('brand', 'user', 'recommended_template')
    serializer_class = TemplateRecommendationSerializer
    permission_classes = [IsAuthenticated, IsBrandMember]
    filterset_class = TemplateRecommendationFilter
    ordering = ['-priority', '-confidence_score']
    brand_field = 'brand'
    
    def get_queryset(self):
        """Filtre par user si spécifié"""
        queryset = super().get_queryset()
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        return queryset.filter(is_active=True)
    
    @action(detail=True, methods=['post'])
    def mark_clicked(self, request, pk=None):
        """Marquer recommandation comme cliquée"""
        recommendation = self.get_object()
        recommendation.clicked = True
        recommendation.clicked_at = timezone.now()
        recommendation.save()
        return Response({'status': 'Marqué comme cliqué'})
    
    @action(detail=False, methods=['get'])
    def for_user(self, request):
        """Recommandations pour l'utilisateur connecté"""
        recommendations = self.get_queryset().filter(
            user=request.user
        )[:10]
        serializer = TemplateRecommendationSerializer(recommendations, many=True)
        return Response(serializer.data)

class TemplateInsightViewSet(BrandScopedViewSetMixin, ReadOnlyModelViewSet):
    """Insights automatiques"""
    queryset = TemplateInsight.objects.select_related('template')
    serializer_class = TemplateInsightSerializer
    permission_classes = [IsAuthenticated, IsBrandMember]
    filterset_class = TemplateInsightFilter
    ordering = ['-severity', '-created_at']
    brand_field = 'template__brand'
    
    @action(detail=True, methods=['post'])
    def mark_resolved(self, request, pk=None):
        """Marquer insight comme résolu"""
        insight = self.get_object()
        insight.is_resolved = True
        insight.resolved_at = timezone.now()
        insight.save()
        return Response({'status': 'Insight marqué comme résolu'})
    
    @action(detail=False, methods=['get'])
    def critical(self, request):
        """Insights critiques non résolus"""
        critical_insights = self.get_queryset().filter(
            severity='critical',
            is_resolved=False
        )
        serializer = TemplateInsightSerializer(critical_insights, many=True)
        return Response(serializer.data)

class OptimizationSuggestionViewSet(BrandScopedViewSetMixin, ModelViewSet):
    """Suggestions d'optimisation"""
    queryset = OptimizationSuggestion.objects.select_related('template')
    serializer_class = OptimizationSuggestionSerializer
    permission_classes = [IsAuthenticated, IsBrandMember]
    ordering = ['-estimated_impact', '-created_at']
    brand_field = 'template__brand'
    
    @action(detail=True, methods=['post'])
    def mark_implemented(self, request, pk=None):
        """Marquer suggestion comme implémentée"""
        suggestion = self.get_object()
        suggestion.is_implemented = True
        suggestion.implemented_at = timezone.now()
        suggestion.save()
        return Response({'status': 'Suggestion marquée comme implémentée'})
    
    @action(detail=False, methods=['get'])
    def high_impact(self, request):
        """Suggestions à fort impact non implémentées"""
        high_impact = self.get_queryset().filter(
            estimated_impact='high',
            is_implemented=False
        )
        serializer = OptimizationSuggestionSerializer(high_impact, many=True)
        return Response(serializer.data)

class TrendAnalysisViewSet(ReadOnlyModelViewSet):
    """Analyses de tendances"""
    queryset = TrendAnalysis.objects.all()
    serializer_class = TrendAnalysisSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['-created_at']
    
    @action(detail=False, methods=['get'])
    def latest_trends(self, request):
        """Dernières analyses de tendances"""
        latest_trends = {}
        analysis_types = ['usage_trends', 'performance_trends', 'popularity_shifts']
        
        for analysis_type in analysis_types:
            latest = self.get_queryset().filter(
                analysis_type=analysis_type
            ).first()
            
            if latest:
                latest_trends[analysis_type] = TrendAnalysisSerializer(latest).data
        
        return Response(latest_trends)
