# backend/ai_usage/views/usage_views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from common.views.mixins import BrandScopedViewSetMixin, AnalyticsViewSetMixin
from common.permissions.business_permissions import IsAuthenticated, IsBrandMember

from ..models import AIJobUsage, AIUsageAlert
from ..serializers import AIJobUsageSerializer, AIUsageAlertSerializer
from ..services import UsageService, AlertService

class AIJobUsageViewSet(BrandScopedViewSetMixin, AnalyticsViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """Usage tracking jobs IA"""
    queryset = AIJobUsage.objects.all()
    serializer_class = AIJobUsageSerializer
    permission_classes = [IsAuthenticated, IsBrandMember]
    ordering = ['-created_at']
    
    def get_queryset(self):
        """✅ SUPPRIMER l'override - laisser BrandScopedViewSetMixin gérer"""
        return super().get_queryset().select_related(
            'ai_job', 
            'ai_job__job_type',
            'ai_job__brand'  # ✅ Précharger brand pour éviter N+1
        )
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """GET /usage/usage/dashboard/ - Dashboard usage"""
        days = int(request.query_params.get('days', 30))
        
        # ✅ Utiliser current_brand du middleware
        dashboard = UsageService.get_usage_dashboard(
            brand=getattr(request, 'current_brand', None),
            days=days
        )
        return Response(dashboard)
    
    @action(detail=False, methods=['get'])
    def cost_breakdown(self, request):
        """GET /usage/usage/cost_breakdown/?month=2024-12"""
        from datetime import datetime
        
        month_str = request.query_params.get('month')
        if month_str:
            try:
                month = datetime.strptime(month_str, '%Y-%m').date()
            except ValueError:
                return Response(
                    {'error': 'Invalid month format. Use YYYY-MM'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            month = None
        
        breakdown = UsageService.get_cost_breakdown(
            brand=getattr(request, 'current_brand', None),
            month=month
        )
        return Response(breakdown)

class AIUsageAlertViewSet(viewsets.ModelViewSet):
    """Alertes usage IA"""
    queryset = AIUsageAlert.objects.all()
    serializer_class = AIUsageAlertSerializer
    permission_classes = [IsAuthenticated, IsBrandMember]
    ordering = ['-created_at']
    
    def get_queryset(self):
        """✅ Filtrage par company (pas brand) pour les alertes"""
        user = self.request.user
        if hasattr(user, 'company') and user.company:
            return self.queryset.filter(company=user.company)
        return self.queryset.none()
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """GET /usage/alerts/active/ - Alertes actives"""
        active_alerts = self.get_queryset().filter(is_resolved=False)
        serializer = self.get_serializer(active_alerts, many=True)
        return Response({
            'count': active_alerts.count(),
            'alerts': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """POST /usage/alerts/{id}/resolve/"""
        alert = self.get_object()
        
        success = AlertService.resolve_alert(alert.id, resolved_by=request.user)
        
        if success:
            return Response({'message': 'Alert resolved successfully'})
        else:
            return Response(
                {'error': 'Failed to resolve alert'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def check_alerts(self, request):
        """POST /usage/alerts/check_alerts/ - Vérifier nouvelles alertes"""
        if not hasattr(request.user, 'company') or not request.user.company:
            return Response(
                {'error': 'Company required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        company = request.user.company
        
        # Vérifier tous types d'alertes
        quota_alerts = AlertService.check_quota_alerts(company)
        failure_alerts = AlertService.check_failure_rate_alerts(company)
        usage_alerts = AlertService.check_unusual_usage_alerts(company)
        
        all_alerts = quota_alerts + failure_alerts + usage_alerts
        
        serializer = self.get_serializer(all_alerts, many=True)
        
        return Response({
            'new_alerts_count': len(all_alerts),
            'alerts': serializer.data
        })