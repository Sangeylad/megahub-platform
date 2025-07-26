from django.db import models

# Create your models here.
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from common.models import TimestampedMixin
import uuid

class SubscriberTracking(TimestampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscriber = models.OneToOneField('mailing_contacts_core.EmailSubscriber', on_delete=models.CASCADE)
    total_emails_sent = models.IntegerField(default=0)
    total_emails_opened = models.IntegerField(default=0)
    total_emails_clicked = models.IntegerField(default=0)
    total_emails_bounced = models.IntegerField(default=0)
    total_emails_unsubscribed = models.IntegerField(default=0)
    engagement_score = models.DecimalField(
        max_digits=5, 
        decimal_places=4, 
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    last_email_sent = models.DateTimeField(null=True, blank=True)
    last_email_opened = models.DateTimeField(null=True, blank=True)
    last_email_clicked = models.DateTimeField(null=True, blank=True)
    last_activity_date = models.DateTimeField(null=True, blank=True)
    days_since_last_activity = models.IntegerField(default=0)
    is_engaged = models.BooleanField(default=True)
    segment_tags = models.JSONField(default=list)

    def __str__(self):
        return f"Tracking for {self.subscriber.email}"
