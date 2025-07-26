from django.db import models

# Create your models here.
from django.db import models
from common.models import TimestampedMixin
import uuid

# Choices
TRIGGER_TYPES = [
    ('subscriber_added', 'Subscriber Added'),
    ('email_opened', 'Email Opened'),
    ('email_clicked', 'Email Clicked'),
    ('date_based', 'Date Based'),
    ('custom_event', 'Custom Event'),
    ('form_submitted', 'Form Submitted'),
    ('tag_added', 'Tag Added'),
    ('list_joined', 'List Joined'),
    ('purchase_made', 'Purchase Made'),
    ('website_visit', 'Website Visit'),
]

class AutomationTrigger(TimestampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    automation = models.ForeignKey('mailing_automations_core.Automation', on_delete=models.CASCADE, related_name='triggers')
    trigger_name = models.CharField(max_length=100)
    trigger_type = models.CharField(max_length=30, choices=TRIGGER_TYPES)
    trigger_conditions = models.JSONField(default=dict)
    delay_amount = models.IntegerField(default=0)
    delay_unit = models.CharField(max_length=20, default='minutes')  # minutes, hours, days
    is_active = models.BooleanField(default=True)
    trigger_count = models.IntegerField(default=0)
    last_triggered = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.trigger_name} - {self.automation.name}"
