from django.db import models

# Create your models here.
from django.db import models
from common.models import TimestampedMixin
import uuid

# Choices
VERIFICATION_STATUSES = [
    ('pending', 'Pending'),
    ('verified', 'Verified'),
    ('failed', 'Failed'),
    ('expired', 'Expired'),
]

RECORD_TYPES = [
    ('SPF', 'SPF'),
    ('DKIM', 'DKIM'),
    ('DMARC', 'DMARC'),
    ('MX', 'MX'),
    ('A', 'A'),
    ('CNAME', 'CNAME'),
    ('TXT', 'TXT'),
]

class EmailAuthentication(TimestampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    config = models.OneToOneField('mailing_deliverability_core.DeliverabilityConfig', on_delete=models.CASCADE)
    spf_status = models.CharField(max_length=20, choices=VERIFICATION_STATUSES, default='pending')
    spf_record = models.TextField(blank=True)
    spf_last_check = models.DateTimeField(null=True, blank=True)
    dkim_status = models.CharField(max_length=20, choices=VERIFICATION_STATUSES, default='pending')
    dkim_selector = models.CharField(max_length=50, blank=True)
    dkim_public_key = models.TextField(blank=True)
    dkim_last_check = models.DateTimeField(null=True, blank=True)
    dmarc_status = models.CharField(max_length=20, choices=VERIFICATION_STATUSES, default='pending')
    dmarc_record = models.TextField(blank=True)
    dmarc_last_check = models.DateTimeField(null=True, blank=True)
    authentication_score = models.IntegerField(default=0)
    last_validation = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Auth for {self.config.brand.name}"

class DNSRecord(TimestampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    authentication = models.ForeignKey(EmailAuthentication, on_delete=models.CASCADE, related_name='dns_records')
    hostname = models.CharField(max_length=255)
    record_type = models.CharField(max_length=10, choices=RECORD_TYPES)
    value = models.TextField()
    ttl = models.IntegerField(default=3600)
    status = models.CharField(max_length=20, choices=VERIFICATION_STATUSES, default='pending')
    last_verified = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    def __str__(self):
        return f"{self.hostname} ({self.record_type})"
