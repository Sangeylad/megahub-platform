# backend/task_scheduling/services/calendar_service.py

from typing import Dict, List, Any, Optional
from django.db.models import Count
from django.utils import timezone
from datetime import datetime, timedelta
from ..models import TaskCalendar, PeriodicTask, CalendarTask

class CalendarService:
    """Service pour la gestion des calendriers de tâches"""
    
    @staticmethod
    def create_calendar(
        name: str,
        brand_id: int,
        description: str = '',
        color: str = '#6366f1',
        default_timezone: str = 'UTC'
    ) -> TaskCalendar:
        """Crée un nouveau calendrier"""
        
        return TaskCalendar.objects.create(
            name=name,
            brand_id=brand_id,
            description=description,
            color=color,
            default_timezone=default_timezone
        )
    
    @staticmethod
    def add_task_to_calendar(
        calendar: TaskCalendar,
        periodic_task: PeriodicTask,
        custom_cron: str = '',
        custom_config: Dict[str, Any] = None
    ) -> CalendarTask:
        """Ajoute une tâche à un calendrier"""
        
        calendar_task, created = CalendarTask.objects.get_or_create(
            calendar=calendar,
            periodic_task=periodic_task,
            defaults={
                'custom_cron': custom_cron,
                'custom_config': custom_config or {},
                'is_active_in_calendar': True
            }
        )
        
        return calendar_task
    
    @staticmethod
    def get_calendar_schedule(
        calendar: TaskCalendar,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Retourne le planning d'un calendrier sur une période"""
        
        schedule = []
        
        # Récupérer toutes les tâches actives du calendrier
        calendar_tasks = CalendarTask.objects.filter(
            calendar=calendar,
            is_active_in_calendar=True,
            periodic_task__is_active=True
        ).select_related('periodic_task', 'periodic_task__base_task')
        
        for calendar_task in calendar_tasks:
            periodic_task = calendar_task.periodic_task
            
            # Utiliser cron custom si défini, sinon celui de la tâche
            cron_expr = calendar_task.custom_cron or periodic_task.cron_expression
            
            # Calculer les occurrences dans la période
            occurrences = CalendarService._calculate_occurrences(
                cron_expr, start_date, end_date
            )
            
            for occurrence in occurrences:
                schedule.append({
                    'task_id': periodic_task.base_task.task_id,
                    'task_type': periodic_task.base_task.task_type,
                    'task_description': periodic_task.base_task.description,
                    'scheduled_at': occurrence.isoformat(),
                    'calendar_task_id': calendar_task.id,
                    'custom_config': calendar_task.custom_config
                })
        
        # Trier par date
        schedule.sort(key=lambda x: x['scheduled_at'])
        
        return schedule
    
    @staticmethod
    def _calculate_occurrences(
        cron_expr: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[datetime]:
        """Calcule les occurrences d'une expression cron sur une période"""
        
        from croniter import croniter
        
        occurrences = []
        cron = croniter(cron_expr, start_date)
        
        # Limite de sécurité pour éviter les boucles infinies
        max_occurrences = 1000
        count = 0
        
        while count < max_occurrences:
            next_run = cron.get_next(datetime)
            
            if next_run > end_date:
                break
            
            occurrences.append(next_run)
            count += 1
        
        return occurrences
    
    @staticmethod
    def get_calendar_stats(calendar: TaskCalendar) -> Dict[str, Any]:
        """Statistiques d'un calendrier"""
        
        stats = CalendarTask.objects.filter(calendar=calendar).aggregate(
            total_tasks=Count('id'),
            active_tasks=Count('id', filter=models.Q(is_active_in_calendar=True))
        )
        
        # Prochaines exécutions (7 jours)
        next_week = timezone.now() + timedelta(days=7)
        upcoming_schedule = CalendarService.get_calendar_schedule(
            calendar, timezone.now(), next_week
        )
        
        stats['upcoming_executions_count'] = len(upcoming_schedule)
        stats['next_execution'] = upcoming_schedule[0] if upcoming_schedule else None
        
        return stats
