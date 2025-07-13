# backend/ai_usage/models/usage_models.py

from django.db import models
from common.models.mixins import TimestampedMixin

class AIJobUsage(TimestampedMixin):
    """Tracking usage et coûts par job IA"""
    ai_job = models.OneToOneField(
        'ai_core.AIJob',
        on_delete=models.CASCADE,
        related_name='usage'
    )
    
    # Métriques tokens
    input_tokens = models.IntegerField(default=0)
    output_tokens = models.IntegerField(default=0)
    total_tokens = models.IntegerField(default=0)
    
    # Métriques coût
    cost_input = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    cost_output = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    
    # Métriques performance
    execution_time_seconds = models.IntegerField(default=0)
    memory_usage_mb = models.IntegerField(default=0)
    
    # Provider info
    provider_name = models.CharField(max_length=50)
    model_name = models.CharField(max_length=100)
    
    # Qualité
    success_rate = models.FloatField(default=1.0)
    error_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'ai_job_usage'
        indexes = [
            models.Index(fields=['provider_name', 'created_at']),
            # ✅ GARDER seulement l'index direct (pas via relation)
            models.Index(fields=['ai_job', 'created_at']),
        ]
    
    def __str__(self):
        return f"Usage {self.ai_job.job_id}"

# AIUsageAlert reste identique

class AIUsageAlert(TimestampedMixin):
   """Alertes usage et coûts"""
   company = models.ForeignKey('company_core.Company', on_delete=models.CASCADE)
   provider_name = models.CharField(max_length=50)
   
   alert_type = models.CharField(max_length=30, choices=[
       ('quota_warning', 'Quota Warning 80%'),
       ('quota_exceeded', 'Quota Exceeded'),
       ('cost_warning', 'Cost Warning'),
       ('high_failure_rate', 'High Failure Rate'),
       ('unusual_usage', 'Unusual Usage Pattern')
   ])
   
   threshold_value = models.DecimalField(max_digits=10, decimal_places=2)
   current_value = models.DecimalField(max_digits=10, decimal_places=2)
   
   message = models.TextField()
   is_resolved = models.BooleanField(default=False)
   resolved_at = models.DateTimeField(null=True, blank=True)
   
   # Notification
   email_sent = models.BooleanField(default=False)
   email_sent_at = models.DateTimeField(null=True, blank=True)
   
   class Meta:
       db_table = 'ai_usage_alert'
       ordering = ['-created_at']
   
   def __str__(self):
       return f"Alert {self.company.name} - {self.alert_type}"
