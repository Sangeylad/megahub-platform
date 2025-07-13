# backend/task_scheduling/serializers/scheduling_serializers.py

from rest_framework import serializers
from common.serializers.mixins import DynamicFieldsSerializer
from task_core.serializers import BaseTaskSerializer
from ..models import PeriodicTask, CronJob, TaskCalendar, CalendarTask

class PeriodicTaskSerializer(DynamicFieldsSerializer):
    """Serializer pour PeriodicTask"""
    
    base_task = BaseTaskSerializer(read_only=True)
    next_runs = serializers.SerializerMethodField()
    
    class Meta:
        model = PeriodicTask
        fields = '__all__'
        read_only_fields = ['next_run_at', 'last_run_at', 'executions_count']
    
    def get_next_runs(self, obj):
        """Calcule les 3 prochaines exécutions"""
        if not obj.cron_expression or not obj.is_active:
            return []
        
        try:
            from croniter import croniter
            from django.utils import timezone
            
            cron = croniter(obj.cron_expression, timezone.now())
            return [cron.get_next(timezone.datetime).isoformat() for _ in range(3)]
        except:
            return []

class CronJobSerializer(DynamicFieldsSerializer):
    """Serializer pour CronJob"""
    
    cron_expression = serializers.SerializerMethodField()
    
    class Meta:
        model = CronJob
        fields = '__all__'
        read_only_fields = [
            'last_execution_at', 'total_executions', 
            'successful_executions', 'failed_executions'
        ]
    
    def get_cron_expression(self, obj):
        """Retourne l'expression cron calculée"""
        return obj.get_cron_expression()

class CalendarTaskSerializer(serializers.ModelSerializer):
    """Serializer pour CalendarTask"""
    
    periodic_task = PeriodicTaskSerializer(read_only=True)
    
    class Meta:
        model = CalendarTask
        fields = '__all__'

class TaskCalendarSerializer(DynamicFieldsSerializer):
    """Serializer pour TaskCalendar"""
    
    tasks_count = serializers.SerializerMethodField()
    active_tasks_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TaskCalendar
        fields = '__all__'
    
    def get_tasks_count(self, obj):
        """Nombre total de tâches dans le calendrier"""
        return obj.calendartask_set.count()
    
    def get_active_tasks_count(self, obj):
        """Nombre de tâches actives dans le calendrier"""
        return obj.calendartask_set.filter(
            is_active_in_calendar=True,
            periodic_task__is_active=True
        ).count()
