from django.db import models

# Create your models here.
from django.db import models
from common.models import TimestampedMixin
import uuid

# Choices
ACCOUNT_STATUSES = [
    ('active', 'Active'),
    ('suspended', 'Suspended'),
    ('trial', 'Trial'),
    ('cancelled', 'Cancelled'),
]

PLAN_TYPES = [
    ('starter', 'Starter'),
    ('professional', 'Professional'),
    ('enterprise', 'Enterprise'),
    ('custom', 'Custom'),
]

class MailingAccount(TimestampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brand = models.OneToOneField('brands_core.Brand', on_delete=models.CASCADE)
    account_status = models.CharField(max_length=20, choices=ACCOUNT_STATUSES, default='active')
    plan_type = models.CharField(max_length=30, choices=PLAN_TYPES, default='starter')
    monthly_send_limit = models.IntegerField(default=10000)
    current_month_sent = models.IntegerField(default=0)
    subscriber_limit = models.IntegerField(default=2000)
    current_subscribers = models.IntegerField(default=0)
    features_enabled = models.JSONField(default=dict)
    timezone = models.CharField(max_length=50, default='Europe/Paris')
    default_from_name = models.CharField(max_length=100, blank=True)
    default_from_email = models.EmailField(blank=True)
    default_reply_to = models.EmailField(blank=True)
    compliance_settings = models.JSONField(default=dict)

    def __str__(self):
        return f"Mailing Account for {self.brand.name}"
