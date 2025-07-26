from django.db import models

# Create your models here.
from django.db import models
from common.models import TimestampedMixin
import uuid

# Choices
EVENT_TYPES = [
    ('sent', 'Sent'),
    ('delivered', 'Delivered'),
    ('opened', 'Opened'),
    ('clicked', 'Clicked'),
    ('bounced', 'Bounced'),
    ('unsubscribed', 'Unsubscribed'),
    ('complained', 'Complained'),
    ('converted', 'Converted'),
]

class EmailEvent(TimestampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES)
    subscriber = models.ForeignKey('mailing_contacts_core.EmailSubscriber', on_delete=models.CASCADE)
    campaign = models.ForeignKey('mailing_campaigns_core.Campaign', on_delete=models.SET_NULL, null=True, blank=True)
    automation = models.ForeignKey('mailing_automations_core.Automation', on_delete=models.SET_NULL, null=True, blank=True)
    email_address = models.EmailField()
    timestamp = models.DateTimeField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict)
    processed = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['event_type', 'timestamp']),
            models.Index(fields=['subscriber']),
            models.Index(fields=['campaign']),
        ]

    def __str__(self):
        return f"{self.event_type} - {self.email_address}"
