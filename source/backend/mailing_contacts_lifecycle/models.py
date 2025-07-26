from django.db import models

# Create your models here.
from django.db import models
from common.models import TimestampedMixin
import uuid

# Choices
LIFECYCLE_STAGES = [
    ('subscriber', 'Subscriber'),
    ('lead', 'Lead'),
    ('qualified_lead', 'Qualified Lead'),
    ('opportunity', 'Opportunity'),
    ('customer', 'Customer'),
    ('advocate', 'Advocate'),
    ('churned', 'Churned'),
]

class SubscriberLifecycle(TimestampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscriber = models.OneToOneField('mailing_contacts_core.EmailSubscriber', on_delete=models.CASCADE)
    current_stage = models.CharField(max_length=30, choices=LIFECYCLE_STAGES, default='subscriber')
    previous_stage = models.CharField(max_length=30, blank=True)
    stage_entered_date = models.DateTimeField(auto_now_add=True)
    days_in_current_stage = models.IntegerField(default=0)
    total_stage_changes = models.IntegerField(default=0)
    first_conversion_date = models.DateTimeField(null=True, blank=True)
    last_conversion_date = models.DateTimeField(null=True, blank=True)
    conversion_count = models.IntegerField(default=0)
    attribution_campaign = models.ForeignKey(
        'mailing_campaigns_core.Campaign', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    attribution_source = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.subscriber.email} - {self.current_stage}"
