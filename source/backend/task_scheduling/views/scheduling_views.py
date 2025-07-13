# backend/task_scheduling/views/scheduling_views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta, datetime
from common.views.mixins import BrandScopedViewSetMixin
from common.permissions.business_permissions import IsAuthenticated, IsBrandMember, IsBrandAdmin
from ..models import PeriodicTask, CronJob, TaskCalendar
from ..serializers import PeriodicTaskSerializer, CronJobSerializer, TaskCalendarSerializer
from ..services import SchedulerService, CalendarService

class PeriodicTaskViewSet(BrandScopedViewSetMixin, viewsets.ModelViewSet):
    """CRUD pour tâches périodiques"""
    
    queryset = PeriodicTask.objects.all()
    serializer_class = PeriodicTaskSerializer
    permission_classes = [IsAuthenticated, IsBrandMember]
    ordering = ['-created_at']
    
    def get_queryset(self):
        return super().get_queryset().select_related(
            'base_task', 'base_task__brand'
        )
    
    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """Met en pause une tâche périodique"""
        periodic_task = self.get_object()
        
        success = SchedulerService.pause_periodic_task(periodic_task.id)
        
        if success:
            return Response({'status': 'Task paused'})
        return Response({'error': 'Failed to pause task'}, status=status.HTTP_400_BAD_REQUEST)
    
    
    
    @action(detail=True, methods=['post'])
    def resume(self, request, pk=None):
        """Reprend une tâche périodique"""
        periodic_task = self.get_object()
        
        success = SchedulerService.resume_periodic_task(periodic_task.id)
        
        if success:
            return Response({'status': 'Task resumed'})
        return Response({'error': 'Failed to resume task'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], url_path='ready-for-execution')
    def ready_for_execution(self, request):
        """Tâches prêtes à être exécutées"""
        ready_tasks = SchedulerService.get_tasks_ready_for_execution()
        
        # Filtrer par brand si nécessaire
        brand_id = getattr(request, 'current_brand', None)
        if brand_id:
            ready_tasks = [
                task for task in ready_tasks 
                if task.base_task.brand_id == brand_id.id
            ]
        
        serializer = self.get_serializer(ready_tasks, many=True)
        return Response({
            'count': len(ready_tasks),
            'tasks': serializer.data
        })
    
    @action(detail=False, methods=['post'], url_path='validate-cron')
    def validate_cron(self, request):
        """Valide une expression cron"""
        cron_expr = request.data.get('cron_expression')
        
        if not cron_expr:
            return Response(
                {'error': 'cron_expression is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        validation = SchedulerService.validate_cron_expression(cron_expr)
        return Response(validation)

class CronJobViewSet(BrandScopedViewSetMixin, viewsets.ModelViewSet):
    """CRUD pour jobs cron"""
    
    queryset = CronJob.objects.all()
    serializer_class = CronJobSerializer
    permission_classes = [IsAuthenticated, IsBrandMember]
    ordering = ['-created_at']
    
    @action(detail=True, methods=['post'])
    def execute_now(self, request, pk=None):
        """Exécute immédiatement un job cron"""
        cron_job = self.get_object()
        
        # Créer une tâche immédiate basée sur le cron job
        from task_core.services import TaskExecutor
        
        immediate_task = TaskExecutor.create_task(
            task_type=cron_job.task_type,
            brand_id=cron_job.brand_id,
            created_by_id=request.user.id,
            context_data={
                'manual_execution': True,
                'cron_job_id': cron_job.id,
                **cron_job.task_config
            },
            priority='high',
            description=f'Manual execution of {cron_job.name}'
        )
        
        # Mettre à jour les stats du cron job
        cron_job.total_executions += 1
        cron_job.last_execution_at = timezone.now()
        cron_job.save(update_fields=['total_executions', 'last_execution_at'])
        
        return Response({
            'message': 'Job executed manually',
            'task_id': immediate_task.task_id
        })

class TaskCalendarViewSet(BrandScopedViewSetMixin, viewsets.ModelViewSet):
    """CRUD pour calendriers de tâches"""
    
    queryset = TaskCalendar.objects.all()
    serializer_class = TaskCalendarSerializer
    permission_classes = [IsAuthenticated, IsBrandMember]
    ordering = ['-created_at']
    
    @action(detail=True, methods=['get'])
    def schedule(self, request, pk=None):
        """Planning du calendrier"""
        calendar = self.get_object()
        
        # Paramètres de date
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        
        if start_date_str:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
        else:
            start_date = timezone.now()
        
        if end_date_str:
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
        else:
            end_date = start_date + timedelta(days=30)  # 30 jours par défaut
        
        schedule = CalendarService.get_calendar_schedule(calendar, start_date, end_date)
        
        return Response({
            'calendar_id': calendar.id,
            'calendar_name': calendar.name,
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'schedule': schedule,
            'total_executions': len(schedule)
        })
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Statistiques du calendrier"""
        calendar = self.get_object()
        
        stats = CalendarService.get_calendar_stats(calendar)
        return Response(stats)
    
    @action(detail=True, methods=['post'])
    def add_task(self, request, pk=None):
        """Ajoute une tâche au calendrier"""
        calendar = self.get_object()
        
        periodic_task_id = request.data.get('periodic_task_id')
        custom_cron = request.data.get('custom_cron', '')
        custom_config = request.data.get('custom_config', {})
        
        try:
            from ..models import PeriodicTask
            periodic_task = PeriodicTask.objects.get(id=periodic_task_id)
            
            calendar_task = CalendarService.add_task_to_calendar(
                calendar=calendar,
                periodic_task=periodic_task,
                custom_cron=custom_cron,
                custom_config=custom_config
            )
            
            return Response({
                'message': 'Task added to calendar',
                'calendar_task_id': calendar_task.id
            })
            
        except PeriodicTask.DoesNotExist:
            return Response(
                {'error': 'Periodic task not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
