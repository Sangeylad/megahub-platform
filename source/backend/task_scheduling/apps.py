# backend/task_scheduling/apps.py

from django.apps import AppConfig

class TaskSchedulingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'task_scheduling'
    verbose_name = 'Task Scheduling & Cron'
