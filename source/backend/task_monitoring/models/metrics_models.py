# backend/task_monitoring/models/metrics_models.py

from django.db import models
from django.contrib.auth import get_user_model
from common.models.mixins import TimestampedMixin, BrandScopedMixin
from task_core.models import BaseTask

User = get_user_model()

class TaskMetrics(TimestampedMixin):
    """
    Extension OneToOne de BaseTask pour métriques performance
    """
    
    # Relation vers BaseTask (hub central)
    base_task = models.OneToOneField(
        BaseTask, 
        on_delete=models.CASCADE, 
        related_name='metrics'
    )
    
    # Métriques d'exécution
    execution_time_ms = models.PositiveIntegerField(null=True, blank=True)
    memory_usage_mb = models.PositiveIntegerField(null=True, blank=True)
    cpu_usage_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Métriques réseau et I/O
    network_bytes_sent = models.PositiveIntegerField(default=0)
    network_bytes_received = models.PositiveIntegerField(default=0)
    disk_io_bytes = models.PositiveIntegerField(default=0)
    
    # Métriques API et coûts
    api_calls_count = models.PositiveIntegerField(default=0)
    tokens_used = models.PositiveIntegerField(default=0)
    cost_usd = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    
    # Erreurs et retry
    error_count = models.PositiveIntegerField(default=0)
    warning_count = models.PositiveIntegerField(default=0)
    retry_count = models.PositiveIntegerField(default=0)
    
    # Worker info
    worker_name = models.CharField(max_length=100, blank=True)
    queue_wait_time_ms = models.PositiveIntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'task_metrics'
        indexes = [
            models.Index(fields=['execution_time_ms']),
            models.Index(fields=['memory_usage_mb']),
            models.Index(fields=['cost_usd']),
            models.Index(fields=['base_task', 'created_at']),
        ]
        
    def __str__(self):
        return f"Metrics: {self.base_task.task_id}"

class AlertRule(TimestampedMixin, BrandScopedMixin):
    """Règles d'alerting pour monitoring"""
    
    METRIC_CHOICES = [
        ('execution_time_ms', 'Temps d\'exécution (ms)'),
        ('memory_usage_mb', 'Mémoire (MB)'),
        ('error_count', 'Nombre d\'erreurs'),
        ('cost_usd', 'Coût USD'),
        ('queue_wait_time_ms', 'Temps d\'attente queue (ms)'),
    ]
    
    CONDITION_CHOICES = [
        ('gt', 'Supérieur à'),
        ('gte', 'Supérieur ou égal à'),
        ('lt', 'Inférieur à'),
        ('lte', 'Inférieur ou égal à'),
        ('eq', 'Égal à'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    metric_field = models.CharField(max_length=50, choices=METRIC_CHOICES)
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)
    threshold_value = models.DecimalField(max_digits=15, decimal_places=4)
    
    # Configuration alerte
    is_active = models.BooleanField(default=True)
    task_types = models.JSONField(default=list, help_text="Types de tâches concernées")
    notification_emails = models.JSONField(default=list)
    webhook_url = models.URLField(blank=True)
    
    # Throttling
    cooldown_minutes = models.PositiveIntegerField(default=60)
    last_triggered_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'task_alert_rule'
        indexes = [
            models.Index(fields=['is_active', 'metric_field']),
            models.Index(fields=['brand', 'is_active']),
        ]
        
    def __str__(self):
        return f"Alert: {self.name}"

class WorkerHealth(TimestampedMixin):
    """Santé des workers Celery"""
    
    worker_name = models.CharField(max_length=100, unique=True)
    queue_name = models.CharField(max_length=50)
    is_online = models.BooleanField(default=True)
    
    # Métriques worker
    active_tasks = models.PositiveIntegerField(default=0)
    processed_tasks = models.PositiveIntegerField(default=0)
    failed_tasks = models.PositiveIntegerField(default=0)
    
    # Ressources système
    cpu_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    memory_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    load_average = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Heartbeat
    last_heartbeat = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'task_worker_health'
        indexes = [
            models.Index(fields=['is_online', 'queue_name']),
            models.Index(fields=['last_heartbeat']),
        ]
        
    def __str__(self):
        return f"Worker: {self.worker_name}"
