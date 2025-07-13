# backend/task_core/services/task_executor.py

import uuid
from typing import Dict, Any, Optional
from celery import current_app
from django.conf import settings
from ..models import BaseTask, TaskType

class TaskExecutor:
    """Service central pour l'exécution des tâches"""
    
    @staticmethod
    def create_task(
        task_type: str,
        brand_id: int,
        created_by_id: int,
        context_data: Dict[str, Any] = None,
        priority: str = 'normal',
        description: str = ''
    ) -> BaseTask:
        """Crée une nouvelle tâche avec ID unique"""
        
        task_id = f"{task_type}_{uuid.uuid4().hex[:8]}"
        
        # Récupérer ou créer le type de tâche
        task_type_obj, _ = TaskType.objects.get_or_create(
            name=task_type,
            defaults={
                'default_queue_id': 1,  # Queue normal par défaut
                'description': f'Task type: {task_type}'
            }
        )
        
        return BaseTask.objects.create(
            task_id=task_id,
            task_type=task_type,
            brand_id=brand_id,
            created_by_id=created_by_id,
            priority=priority,
            queue_name=task_type_obj.default_queue.name,
            context_data=context_data or {},
            description=description
        )
    
    @staticmethod
    def route_to_queue(task_type: str, priority: str = 'normal') -> str:
        """Détermine la queue optimale selon type et priorité"""
        
        queue_mapping = {
            'high': 'high_priority',
            'critical': 'high_priority',
            'normal': 'normal',
            'low': 'low_priority'
        }
        
        # Types spéciaux vers queues dédiées
        if 'ai_' in task_type or 'content_generation' in task_type:
            return 'ai_processing' if priority == 'high' else 'normal'
            
        return queue_mapping.get(priority, 'normal')
