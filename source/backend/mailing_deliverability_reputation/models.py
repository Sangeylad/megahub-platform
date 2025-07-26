from django.db import models

# Create your models here.
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from common.models import TimestampedMixin
import uuid

class DomainReputation(TimestampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    config = models.ForeignKey('mailing_deliverability_core.DeliverabilityConfig', on_delete=models.CASCADE, related_name='reputation_history')
    monitoring_date = models.DateField()
    reputation_score = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    sender_score = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    bounce_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=4, 
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    complaint_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=4, 
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    spam_trap_hits = models.IntegerField(default=0)
    blacklist_status = models.JSONField(default=dict)
    deliverability_issues = models.JSONField(default=list)
    recommendations = models.TextField(blank=True)

    class Meta:
        unique_together = [['config', 'monitoring_date']]

    def __str__(self):
        return f"Reputation {self.config.brand.name} - {self.monitoring_date}"
