# backend/task_core/celery_config.py

from celery import Celery
from kombu import Exchange, Queue
from django.conf import settings

# Configuration des queues avec priorité
task_routes = {
    # Tasks haute priorité
    'ai_*': {'queue': 'high_priority'},
    'notification_*': {'queue': 'high_priority'},
    'user_facing_*': {'queue': 'high_priority'},
    
    # Tasks normales
    'content_*': {'queue': 'normal'},
    'seo_*': {'queue': 'normal'},
    'blog_*': {'queue': 'normal'},
    
    # Tasks lourdes
    'batch_*': {'queue': 'low_priority'},
    'analytics_*': {'queue': 'low_priority'},
    'cleanup_*': {'queue': 'low_priority'},
}

# Définition des queues
task_queues = (
    Queue('high_priority', Exchange('high_priority'), routing_key='high_priority',
          queue_arguments={'x-max-priority': 10}),
    Queue('normal', Exchange('normal'), routing_key='normal',
          queue_arguments={'x-max-priority': 5}),
    Queue('low_priority', Exchange('low_priority'), routing_key='low_priority',
          queue_arguments={'x-max-priority': 1}),
)

# Configuration worker
worker_prefetch_multiplier = 1
task_acks_late = True
worker_max_tasks_per_child = 1000
task_time_limit = 3600  # 1 heure
task_soft_time_limit = 3300  # 55 minutes
