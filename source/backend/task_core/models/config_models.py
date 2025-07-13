# backend/task_core/models/config_models.py

from django.db import models
from common.models.mixins import TimestampedMixin

class TaskQueue(TimestampedMixin):
    """Configuration des queues Celery"""
    
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    concurrency = models.PositiveIntegerField(default=2)
    max_memory_mb = models.PositiveIntegerField(default=512)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'task_queue'
        
    def __str__(self):
        return self.name

class TaskType(TimestampedMixin):
    """Types de tâches supportés"""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    default_queue = models.ForeignKey(TaskQueue, on_delete=models.CASCADE)
    default_priority = models.CharField(max_length=20, default='normal')
    timeout_seconds = models.PositiveIntegerField(default=3600)
    max_retries = models.PositiveIntegerField(default=3)
    
    class Meta:
        db_table = 'task_type'
        
    def __str__(self):
        return self.name
