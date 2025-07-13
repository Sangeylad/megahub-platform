# backend/task_core/services/queue_manager.py

from typing import Dict, List
from django.db import models  # ✅ AJOUT
from django.db.models import Count, Avg
from ..models import BaseTask, TaskQueue

class QueueManager:
    """Gestion des queues et métriques"""
    
    @staticmethod
    def get_queue_stats() -> Dict[str, Dict[str, int]]:
        """Statistiques en temps réel des queues"""
        
        stats = {}
        queues = TaskQueue.objects.filter(is_active=True)
        
        for queue in queues:
            queue_stats = BaseTask.objects.filter(
                queue_name=queue.name
            ).aggregate(
                total=Count('id'),
                pending=Count('id', filter=models.Q(status='pending')),
                processing=Count('id', filter=models.Q(status='processing')),
                completed=Count('id', filter=models.Q(status='completed')),
                failed=Count('id', filter=models.Q(status='failed'))
            )
            
            stats[queue.name] = queue_stats
            
        return stats
    
    @staticmethod
    def get_recommended_queue(brand_id: int, task_type: str) -> str:
        """Recommande la queue optimale selon charge actuelle"""
        
        # Logique intelligente selon charge
        queue_loads = QueueManager.get_queue_stats()
        
        # Si high_priority surchargée, utiliser normal
        if queue_loads.get('high_priority', {}).get('pending', 0) > 50:
            return 'normal'
            
        return TaskExecutor.route_to_queue(task_type)
