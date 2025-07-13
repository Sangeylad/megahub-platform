# backend/task_scheduling/services/scheduler_service.py

from typing import Dict, List, Any, Optional
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from task_core.services import TaskExecutor
from ..models import PeriodicTask, CronJob
from croniter import croniter

class SchedulerService:
    """Service pour la gestion du scheduling"""
    
    @staticmethod
    @transaction.atomic
    def create_periodic_task(
        task_type: str,
        brand_id: int,
        created_by_id: int,
        cron_expression: str,
        schedule_config: Dict[str, Any] = None,
        description: str = '',
        start_date = None,
        end_date = None,
        max_executions: Optional[int] = None
    ) -> PeriodicTask:
        """Crée une tâche périodique"""
        
        # Créer la BaseTask
        base_task = TaskExecutor.create_task(
            task_type=task_type,
            brand_id=brand_id,
            created_by_id=created_by_id,
            context_data={'periodic': True},
            priority='normal',
            description=description or f'Periodic {task_type}'
        )
        
        # Créer la PeriodicTask
        periodic_task = PeriodicTask.objects.create(
            base_task=base_task,
            cron_expression=cron_expression,
            start_date=start_date or timezone.now(),
            end_date=end_date,
            max_executions=max_executions,
            schedule_config=schedule_config or {}
        )
        
        return periodic_task
    
    @staticmethod
    def get_tasks_ready_for_execution() -> List[PeriodicTask]:
        """Retourne les tâches prêtes à être exécutées"""
        
        now = timezone.now()
        
        ready_tasks = PeriodicTask.objects.filter(
            is_active=True,
            next_run_at__lte=now
        ).select_related('base_task', 'base_task__brand')
        
        # Filtrer avec la logique métier
        return [task for task in ready_tasks if task.is_ready_to_run()]
    
    @staticmethod
    def execute_ready_tasks() -> Dict[str, Any]:
        """Exécute toutes les tâches prêtes"""
        
        ready_tasks = SchedulerService.get_tasks_ready_for_execution()
        
        results = {
            'executed': [],
            'failed': [],
            'total': len(ready_tasks)
        }
        
        for periodic_task in ready_tasks:
            try:
                # Créer une nouvelle BaseTask pour cette exécution
                execution_task = TaskExecutor.create_task(
                    task_type=periodic_task.base_task.task_type,
                    brand_id=periodic_task.base_task.brand_id,
                    created_by_id=periodic_task.base_task.created_by_id,
                    context_data={
                        'periodic_execution': True,
                        'periodic_task_id': periodic_task.id,
                        **periodic_task.schedule_config
                    },
                    description=f'Execution of {periodic_task.base_task.task_id}'
                )
                
                # Marquer la tâche périodique comme exécutée
                periodic_task.mark_executed()
                
                results['executed'].append({
                    'periodic_task_id': periodic_task.id,
                    'execution_task_id': execution_task.task_id,
                    'executed_at': timezone.now()
                })
                
            except Exception as e:
                results['failed'].append({
                    'periodic_task_id': periodic_task.id,
                    'error': str(e)
                })
        
        return results
    
    @staticmethod
    def validate_cron_expression(cron_expr: str) -> Dict[str, Any]:
        """Valide une expression cron"""
        
        try:
            # Tester avec croniter
            cron = croniter(cron_expr, timezone.now())
            
            # Calculer les 5 prochaines exécutions
            next_runs = []
            for _ in range(5):
                next_runs.append(cron.get_next(timezone.datetime))
            
            return {
                'is_valid': True,
                'next_executions': [dt.isoformat() for dt in next_runs]
            }
            
        except Exception as e:
            return {
                'is_valid': False,
                'error': str(e)
            }
    
    @staticmethod
    def pause_periodic_task(periodic_task_id: int) -> bool:
        """Met en pause une tâche périodique"""
        
        try:
            periodic_task = PeriodicTask.objects.get(id=periodic_task_id)
            periodic_task.is_active = False
            periodic_task.save(update_fields=['is_active'])
            return True
        except PeriodicTask.DoesNotExist:
            return False
    
    @staticmethod
    def resume_periodic_task(periodic_task_id: int) -> bool:
        """Reprend une tâche périodique"""
        
        try:
            periodic_task = PeriodicTask.objects.get(id=periodic_task_id)
            periodic_task.is_active = True
            periodic_task.calculate_next_run()
            periodic_task.save(update_fields=['is_active', 'next_run_at'])
            return True
        except PeriodicTask.DoesNotExist:
            return False
