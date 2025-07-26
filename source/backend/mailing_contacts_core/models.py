from django.db import models

# Create your models here.
from django.db import models
from django.core.validators import RegexValidator
from common.models import TimestampedMixin
import uuid

# Choices
SUBSCRIBER_STATUSES = [
    ('active', 'Active'),
    ('unsubscribed', 'Unsubscribed'),
    ('bounced', 'Bounced'),
    ('pending', 'Pending'),
    ('complaint', 'Complaint'),
]

SUBSCRIBER_SOURCES = [
    ('manual', 'Manual'),
    ('import', 'Import'),
    ('api', 'API'),
    ('form', 'Form'),
    ('integration', 'Integration'),
    ('crm_sync', 'CRM Sync'),
    ('landing_page', 'Landing Page'),
    ('popup', 'Popup'),
    ('webinar', 'Webinar'),
    ('event', 'Event'),
]

LANGUAGES = [
    ('fr', 'Français'),
    ('en', 'English'),
    ('es', 'Español'),
    ('de', 'Deutsch'),
    ('it', 'Italiano'),
    ('pt', 'Português'),
]

TIMEZONES = [
    ('Europe/Paris', 'Europe/Paris'),
    ('Europe/London', 'Europe/London'),
    ('America/New_York', 'America/New_York'),
    ('America/Los_Angeles', 'America/Los_Angeles'),
    ('Asia/Tokyo', 'Asia/Tokyo'),
    ('Australia/Sydney', 'Australia/Sydney'),
]

class EmailSubscriber(TimestampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone = models.CharField(
        max_length=20, 
        blank=True,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')]
    )
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    company = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=SUBSCRIBER_STATUSES, default='active')
    source_brand = models.ForeignKey('brands_core.Brand', on_delete=models.CASCADE)
    crm_contact = models.OneToOneField(
        'crm_entities_core.Contact', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    source = models.CharField(max_length=50, choices=SUBSCRIBER_SOURCES, default='manual')
    language = models.CharField(max_length=10, choices=LANGUAGES, default='fr')
    timezone = models.CharField(max_length=50, choices=TIMEZONES, default='Europe/Paris')

    class Meta:
        unique_together = [['email', 'source_brand']]
        indexes = [
            models.Index(fields=['status', 'source_brand']),
            models.Index(fields=['email']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.email} ({self.source_brand.name})"
