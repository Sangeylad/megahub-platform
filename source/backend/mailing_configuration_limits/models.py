from django.db import models

# Create your models here.
from django.db import models
from common.models import TimestampedMixin
import uuid

class SendingLimits(TimestampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.OneToOneField('mailing_configuration_core.MailingAccount', on_delete=models.CASCADE)
    hourly_limit = models.IntegerField(default=1000)
    daily_limit = models.IntegerField(default=10000)
    monthly_limit = models.IntegerField(default=100000)
    current_hour_sent = models.IntegerField(default=0)
    current_day_sent = models.IntegerField(default=0)
    current_month_sent = models.IntegerField(default=0)
    hour_reset_time = models.DateTimeField(null=True, blank=True)
    day_reset_time = models.DateTimeField(null=True, blank=True)
    month_reset_time = models.DateTimeField(null=True, blank=True)
    send_rate_per_minute = models.IntegerField(default=100)
    burst_limit = models.IntegerField(default=500)
    alert_threshold_percent = models.IntegerField(default=80)
    last_alert_sent = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Limits for {self.account.brand.name}"
