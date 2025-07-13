# backend/task_monitoring/serializers/monitoring_serializers.py

from rest_framework import serializers
from common.serializers.mixins import DynamicFieldsSerializer
from task_core.serializers import BaseTaskSerializer
from ..models import TaskMetrics, AlertRule, WorkerHealth

class TaskMetricsSerializer(DynamicFieldsSerializer):
    """Serializer pour TaskMetrics"""
    
    base_task = BaseTaskSerializer(read_only=True)
    
    class Meta:
        model = TaskMetrics
        fields = '__all__'

class AlertRuleSerializer(DynamicFieldsSerializer):
    """Serializer pour AlertRule"""
    
    class Meta:
        model = AlertRule
        fields = '__all__'
        read_only_fields = ['last_triggered_at']

class WorkerHealthSerializer(serializers.ModelSerializer):
    """Serializer pour WorkerHealth"""
    
    is_healthy = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkerHealth
        fields = '__all__'
    
    def get_is_healthy(self, obj):
        """Détermine si le worker est en bonne santé"""
        from django.utils import timezone
        from datetime import timedelta
        
        # Critères de santé
        recent_heartbeat = obj.last_heartbeat >= (
            timezone.now() - timedelta(minutes=5)
        )
        reasonable_cpu = obj.cpu_percent < 90
        reasonable_memory = obj.memory_percent < 90
        
        return all([recent_heartbeat, reasonable_cpu, reasonable_memory, obj.is_online])
