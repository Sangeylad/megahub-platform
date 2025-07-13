# backend/task_persistence/apps.py

from django.apps import AppConfig

class TaskPersistenceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'task_persistence'
    verbose_name = 'Task Persistence & Recovery'
