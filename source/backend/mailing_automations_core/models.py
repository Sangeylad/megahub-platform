from django.db import models

# Create your models here.
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from common.models import TimestampedMixin
import uuid

# Choices
AUTOMATION_TYPES = [
    ('drip', 'Drip Campaign'),
    ('welcome', 'Welcome Series'),
    ('abandoned_cart', 'Abandoned Cart'),
    ('reengagement', 'Re-engagement'),
    ('birthday', 'Birthday Campaign'),
    ('anniversary', 'Anniversary'),
    ('educational', 'Educational Series'),
    ('nurturing', 'Lead Nurturing'),
    ('onboarding', 'User Onboarding'),
    ('post_purchase', 'Post Purchase'),
    ('custom', 'Custom Workflow'),
]

AUTOMATION_STATUSES = [
    ('draft', 'Draft'),
    ('active', 'Active'),
    ('paused', 'Paused'),
    ('archived', 'Archived'),
]

class Automation(TimestampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    automation_type = models.CharField(max_length=30, choices=AUTOMATION_TYPES, default='drip')
    status = models.CharField(max_length=20, choices=AUTOMATION_STATUSES, default='draft')
    brand = models.ForeignKey('brands_core.Brand', on_delete=models.CASCADE)
    created_by = models.ForeignKey('users_core.CustomUser', on_delete=models.CASCADE)
    entry_criteria = models.JSONField()
    exit_criteria = models.JSONField(default=dict)
    allow_re_entry = models.BooleanField(default=False)
    re_entry_delay_days = models.IntegerField(default=0)
    total_entries = models.IntegerField(default=0)
    active_subscribers = models.IntegerField(default=0)
    completed_subscribers = models.IntegerField(default=0)
    conversion_goal = models.CharField(max_length=100, blank=True)
    conversion_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=4, 
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )

    class Meta:
        unique_together = [['name', 'brand']]

    def __str__(self):
        return f"{self.name} ({self.brand.name})"
