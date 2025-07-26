from django.db import models

# Create your models here.
from django.db import models
from common.models import TimestampedMixin
import uuid

# Choices
DOMAIN_TYPES = [
    ('sending', 'Sending'),
    ('tracking', 'Tracking'),
    ('unsubscribe', 'Unsubscribe'),
]

VERIFICATION_STATUSES = [
    ('pending', 'Pending'),
    ('verified', 'Verified'),
    ('failed', 'Failed'),
    ('expired', 'Expired'),
]

class DomainConfig(TimestampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey('mailing_configuration_core.MailingAccount', on_delete=models.CASCADE, related_name='domains')
    domain_name = models.CharField(max_length=255)
    domain_type = models.CharField(max_length=30, choices=DOMAIN_TYPES, default='sending')
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUSES, default='pending')
    verification_token = models.CharField(max_length=255, blank=True)
    dns_records = models.JSONField(default=dict)
    ssl_enabled = models.BooleanField(default=False)
    ssl_certificate = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = [['account', 'domain_name']]

    def __str__(self):
        return f"{self.domain_name} ({self.domain_type})"
