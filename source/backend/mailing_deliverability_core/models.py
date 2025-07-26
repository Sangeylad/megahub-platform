from django.db import models

# Create your models here.
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from common.models import TimestampedMixin
import uuid

# Choices
DMARC_POLICIES = [
    ('none', 'None'),
    ('quarantine', 'Quarantine'),
    ('reject', 'Reject'),
]

WARMING_STATUSES = [
    ('not_started', 'Not Started'),
    ('in_progress', 'In Progress'),
    ('completed', 'Completed'),
    ('paused', 'Paused'),
    ('failed', 'Failed'),
]

class DeliverabilityConfig(TimestampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brand = models.OneToOneField('brands_core.Brand', on_delete=models.CASCADE)
    sending_domain = models.CharField(max_length=255)
    return_path_domain = models.CharField(max_length=255, blank=True)
    dedicated_ip = models.GenericIPAddressField(null=True, blank=True)
    shared_ip_pool = models.CharField(max_length=100, blank=True)
    dkim_enabled = models.BooleanField(default=False)
    dkim_selector = models.CharField(max_length=50, blank=True)
    spf_record = models.TextField(blank=True)
    dmarc_policy = models.CharField(max_length=20, choices=DMARC_POLICIES, default='none')
    reputation_score = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    warming_status = models.CharField(max_length=30, choices=WARMING_STATUSES, default='not_started')
    daily_send_limit = models.IntegerField(default=10000)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Deliverability Config for {self.brand.name}"
