from django.db import models

# Create your models here.
from django.db import models
from common.models import TimestampedMixin
import uuid

# Choices
DELIVERY_STATUSES = [
    ('pending', 'Pending'),
    ('processing', 'Processing'),
    ('completed', 'Completed'),
    ('failed', 'Failed'),
    ('cancelled', 'Cancelled'),
]

class CampaignDelivery(TimestampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.OneToOneField('mailing_campaigns_core.Campaign', on_delete=models.CASCADE)
    delivery_status = models.CharField(max_length=30, choices=DELIVERY_STATUSES, default='pending')
    sending_server = models.CharField(max_length=100, blank=True)
    sending_ip = models.GenericIPAddressField(null=True, blank=True)
    total_to_send = models.IntegerField(default=0)
    sent_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    processing_rate = models.IntegerField(default=0)  # Emails/minute
    estimated_completion = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    def __str__(self):
        return f"Delivery for {self.campaign.name}"
