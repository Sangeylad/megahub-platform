from django.db import models

# Create your models here.
from django.db import models
from common.models import TimestampedMixin
import uuid

# Choices
CONVERSION_TYPES = [
    ('purchase', 'Purchase'),
    ('signup', 'Signup'),
    ('download', 'Download'),
    ('demo_request', 'Demo Request'),
    ('trial_start', 'Trial Start'),
    ('form_submit', 'Form Submit'),
    ('page_visit', 'Page Visit'),
    ('custom', 'Custom'),
]

CURRENCIES = [
    ('EUR', 'Euro'),
    ('USD', 'US Dollar'),
    ('GBP', 'British Pound'),
    ('CAD', 'Canadian Dollar'),
    ('AUD', 'Australian Dollar'),
    ('CHF', 'Swiss Franc'),
    ('JPY', 'Japanese Yen'),
]

class EmailConversion(TimestampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email_event = models.OneToOneField('mailing_analytics_core.EmailEvent', on_delete=models.CASCADE)
    conversion_type = models.CharField(max_length=30, choices=CONVERSION_TYPES)
    conversion_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, choices=CURRENCIES, default='EUR')
    conversion_url = models.URLField(blank=True)
    attribution_window_hours = models.IntegerField(default=24)
    time_to_conversion_minutes = models.IntegerField(default=0)
    conversion_metadata = models.JSONField(default=dict)

    def __str__(self):
        return f"Conversion: {self.email_event.email_address} - {self.conversion_type}"
