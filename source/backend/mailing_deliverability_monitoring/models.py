from django.db import models

# Create your models here.
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from common.models import TimestampedMixin
import uuid

class DeliverabilityMonitoring(TimestampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    config = models.ForeignKey('mailing_deliverability_core.DeliverabilityConfig', on_delete=models.CASCADE, related_name='monitoring')
    monitoring_date = models.DateField()
    inbox_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=4, 
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    spam_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=4, 
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    missing_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=4, 
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    avg_delivery_time_minutes = models.IntegerField(default=0)
    gmail_inbox_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=4, 
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    outlook_inbox_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=4, 
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    yahoo_inbox_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=4, 
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    provider_feedback = models.JSONField(default=dict)
    recommendations = models.TextField(blank=True)

    class Meta:
        unique_together = [['config', 'monitoring_date']]

    def __str__(self):
        return f"Monitoring {self.config.brand.name} - {self.monitoring_date}"
