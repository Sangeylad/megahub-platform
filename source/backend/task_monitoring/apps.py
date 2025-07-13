# backend/task_monitoring/apps.py

from django.apps import AppConfig

class TaskMonitoringConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'task_monitoring'
    verbose_name = 'Task Monitoring & Metrics'
