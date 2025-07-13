# backend/task_core/apps.py

from django.apps import AppConfig

class TaskCoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'task_core'
    verbose_name = 'Task Core Infrastructure'
    
    def ready(self):
        """Initialisation des queues par défaut"""
        pass
