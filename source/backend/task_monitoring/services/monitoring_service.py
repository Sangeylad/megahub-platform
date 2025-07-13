# backend/task_monitoring/services/monitoring_service.py

from typing import Dict, Any, List, Optional
from django.db.models import Avg, Count, Sum, Max, Min
from django.utils import timezone
from datetime import timedelta
from task_core.models import BaseTask
from ..models import TaskMetrics, WorkerHealth
from django.db import models

class MonitoringService:
    """Service pour la collecte et analyse des métriques"""
    
    @staticmethod
    def record_task_metrics(
        base_task: BaseTask,
        execution_time_ms: Optional[int] = None,
        memory_usage_mb: Optional[int] = None,
        cpu_usage_percent: Optional[float] = None,
        api_calls_count: int = 0,
        tokens_used: int = 0,
        cost_usd: float = 0,
        worker_name: str = '',
        **kwargs
    ) -> TaskMetrics:
        """Enregistre les métriques d'une tâche"""
        
        metrics, created = TaskMetrics.objects.get_or_create(
            base_task=base_task,
            defaults={
                'execution_time_ms': execution_time_ms,
                'memory_usage_mb': memory_usage_mb,
                'cpu_usage_percent': cpu_usage_percent,
                'api_calls_count': api_calls_count,
                'tokens_used': tokens_used,
                'cost_usd': cost_usd,
                'worker_name': worker_name,
                **kwargs
            }
        )
        
        if not created:
            # Mise à jour si existe déjà
            for field, value in {
                'execution_time_ms': execution_time_ms,
                'memory_usage_mb': memory_usage_mb,
                'cpu_usage_percent': cpu_usage_percent,
                'api_calls_count': api_calls_count,
                'tokens_used': tokens_used,
                'cost_usd': cost_usd,
                'worker_name': worker_name,
                **kwargs
            }.items():
                if value is not None:
                    setattr(metrics, field, value)
            metrics.save()
        
        return metrics
    
    @staticmethod
    def get_dashboard_stats(brand_id: Optional[int] = None, days: int = 7) -> Dict[str, Any]:
        """Statistiques pour dashboard de monitoring"""
        
        since_date = timezone.now() - timedelta(days=days)
        
        # Base queryset
        base_queryset = BaseTask.objects.filter(created_at__gte=since_date)
        if brand_id:
            base_queryset = base_queryset.filter(brand_id=brand_id)
        
        # Statistiques générales
        general_stats = base_queryset.aggregate(
            total_tasks=Count('id'),
            completed_tasks=Count('id', filter=models.Q(status='completed')),
            failed_tasks=Count('id', filter=models.Q(status='failed')),
            processing_tasks=Count('id', filter=models.Q(status='processing')),
            pending_tasks=Count('id', filter=models.Q(status='pending'))
        )
        
        # Métriques de performance
        metrics_queryset = TaskMetrics.objects.filter(
            base_task__in=base_queryset
        ).exclude(execution_time_ms__isnull=True)
        
        performance_stats = metrics_queryset.aggregate(
            avg_execution_time=Avg('execution_time_ms'),
            max_execution_time=Max('execution_time_ms'),
            min_execution_time=Min('execution_time_ms'),
            avg_memory_usage=Avg('memory_usage_mb'),
            total_cost=Sum('cost_usd'),
            total_tokens=Sum('tokens_used'),
            total_api_calls=Sum('api_calls_count')
        )
        
        # Statistiques par type de tâche
        task_type_stats = base_queryset.values('task_type').annotate(
            count=Count('id'),
            completed=Count('id', filter=models.Q(status='completed')),
            failed=Count('id', filter=models.Q(status='failed'))
        ).order_by('-count')[:10]
        
        # Santé des workers
        worker_health = WorkerHealth.objects.filter(
            last_heartbeat__gte=timezone.now() - timedelta(minutes=5)
        ).values(
            'worker_name', 'queue_name', 'is_online', 
            'active_tasks', 'cpu_percent', 'memory_percent'
        )
        
        return {
            'period_days': days,
            'general': general_stats,
            'performance': performance_stats,
            'task_types': list(task_type_stats),
            'workers': list(worker_health),
            'success_rate': (
                general_stats['completed_tasks'] / max(general_stats['total_tasks'], 1)
            ) * 100
        }
    
    @staticmethod
    def get_performance_trends(brand_id: Optional[int] = None, days: int = 30) -> Dict[str, List]:
        """Tendances de performance sur la période"""
        
        since_date = timezone.now() - timedelta(days=days)
        
        queryset = TaskMetrics.objects.filter(
            created_at__gte=since_date  # ✅ Utilise le champ direct
        ).select_related('base_task')
        
        if brand_id:
            queryset = queryset.filter(base_task__brand_id=brand_id)
        
        # ✅ Approche Django native sans extra()
        daily_stats = queryset.values(
            'created_at__date'  # ✅ Django lookup natif
        ).annotate(
            avg_execution_time=Avg('execution_time_ms'),
            avg_memory=Avg('memory_usage_mb'),
            total_cost=Sum('cost_usd'),
            task_count=Count('id')
        ).order_by('created_at__date')
        
        return {
            'daily_performance': list(daily_stats),
            'cost_trend': [
                {'date': stat['created_at__date'], 'cost': float(stat['total_cost'] or 0)}
                for stat in daily_stats
            ]
        }
    
    @staticmethod
    def update_worker_health(
        worker_name: str,
        queue_name: str,
        active_tasks: int = 0,
        cpu_percent: float = 0,
        memory_percent: float = 0,
        **kwargs
    ):
        """Met à jour la santé d'un worker"""
        
        worker, created = WorkerHealth.objects.update_or_create(
            worker_name=worker_name,
            defaults={
                'queue_name': queue_name,
                'is_online': True,
                'active_tasks': active_tasks,
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'last_heartbeat': timezone.now(),
                **kwargs
            }
        )
        
        return worker
