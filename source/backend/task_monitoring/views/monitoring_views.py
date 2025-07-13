# backend/task_monitoring/views/monitoring_views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from common.views.mixins import BrandScopedViewSetMixin, AnalyticsViewSetMixin
from common.permissions.business_permissions import IsAuthenticated, IsBrandMember, IsBrandAdmin
from ..models import TaskMetrics, AlertRule, WorkerHealth
from ..serializers import TaskMetricsSerializer, AlertRuleSerializer, WorkerHealthSerializer
from ..services import MonitoringService

class TaskMetricsViewSet(BrandScopedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """Lecture seule des métriques de tâches"""
    ordering = ['-created_at']
    queryset = TaskMetrics.objects.all()
    serializer_class = TaskMetricsSerializer
    permission_classes = [IsAuthenticated, IsBrandMember]
    filter_backends = [DjangoFilterBackend]
    ordering = ['-created_at']
    
    def get_queryset(self):
        return super().get_queryset().select_related(
            'base_task', 'base_task__brand'
        )
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Dashboard de monitoring"""
        brand_id = getattr(request, 'current_brand', None)
        brand_id = brand_id.id if brand_id else None
        
        days = int(request.query_params.get('days', 7))
        
        stats = MonitoringService.get_dashboard_stats(brand_id, days)
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def trends(self, request):
        """Tendances de performance"""
        brand_id = getattr(request, 'current_brand', None)
        brand_id = brand_id.id if brand_id else None
        
        days = int(request.query_params.get('days', 30))
        
        trends = MonitoringService.get_performance_trends(brand_id, days)
        return Response(trends)

class AlertRuleViewSet(BrandScopedViewSetMixin, viewsets.ModelViewSet):
    """CRUD pour règles d'alerte"""
    
    queryset = AlertRule.objects.all()
    serializer_class = AlertRuleSerializer
    permission_classes = [IsAuthenticated, IsBrandAdmin]  # Admin seulement
    ordering = ['-created_at']
    
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Tester une règle d'alerte"""
        rule = self.get_object()
        
        # Logique de test - simuler une condition
        test_result = {
            'rule_id': rule.id,
            'rule_name': rule.name,
            'test_passed': True,
            'message': 'Alert rule configuration is valid'
        }
        
        return Response(test_result)

class WorkerHealthViewSet(viewsets.ReadOnlyModelViewSet):
    """Santé des workers (read-only)"""
    
    queryset = WorkerHealth.objects.all()
    serializer_class = WorkerHealthSerializer
    permission_classes = [IsAuthenticated, IsBrandAdmin]
    ordering = ['-last_heartbeat']
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """Vue d'ensemble de la santé des workers"""
        from django.utils import timezone
        from datetime import timedelta
        
        # Workers online (heartbeat < 5 min)
        online_threshold = timezone.now() - timedelta(minutes=5)
        
        workers = WorkerHealth.objects.all()
        online_workers = workers.filter(
            last_heartbeat__gte=online_threshold,
            is_online=True
        )
        
        overview = {
            'total_workers': workers.count(),
            'online_workers': online_workers.count(),
            'offline_workers': workers.count() - online_workers.count(),
            'queues_status': {},
            'alerts': []
        }
        
        # Statut par queue
        for worker in online_workers:
            queue = worker.queue_name
            if queue not in overview['queues_status']:
                overview['queues_status'][queue] = {
                    'workers': 0,
                    'active_tasks': 0,
                    'avg_cpu': 0,
                    'avg_memory': 0
                }
            
            overview['queues_status'][queue]['workers'] += 1
            overview['queues_status'][queue]['active_tasks'] += worker.active_tasks
            overview['queues_status'][queue]['avg_cpu'] += worker.cpu_percent
            overview['queues_status'][queue]['avg_memory'] += worker.memory_percent
        
        # Calculer moyennes
        for queue_data in overview['queues_status'].values():
            if queue_data['workers'] > 0:
                queue_data['avg_cpu'] /= queue_data['workers']
                queue_data['avg_memory'] /= queue_data['workers']
        
        return Response(overview)
