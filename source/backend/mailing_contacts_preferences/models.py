from django.db import models

# Create your models here.
from django.db import models
from common.models import TimestampedMixin
import uuid

# Choices
EMAIL_FREQUENCIES = [
    ('daily', 'Daily'),
    ('weekly', 'Weekly'),
    ('bi_weekly', 'Bi-weekly'),
    ('monthly', 'Monthly'),
    ('quarterly', 'Quarterly'),
]

UNSUBSCRIBE_REASONS = [
    ('frequency', 'Too frequent'),
    ('content', 'Content not relevant'),
    ('cost', 'Too expensive'),
    ('spam', 'Considered spam'),
    ('irrelevant', 'Not interested'),
    ('duplicate', 'Already subscribed elsewhere'),
    ('other', 'Other reason'),
]

class SubscriberPreferences(TimestampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscriber = models.OneToOneField('mailing_contacts_core.EmailSubscriber', on_delete=models.CASCADE)
    email_marketing = models.BooleanField(default=True)
    email_transactional = models.BooleanField(default=True)
    email_product_updates = models.BooleanField(default=False)
    email_tips_tricks = models.BooleanField(default=False)
    frequency = models.CharField(max_length=20, choices=EMAIL_FREQUENCIES, default='weekly')
    preferred_send_time = models.TimeField(null=True, blank=True)
    preferred_days = models.JSONField(default=list)  # [1,2,3,4,5] (lundi=1)
    double_optin_confirmed = models.BooleanField(default=False)
    double_optin_date = models.DateTimeField(null=True, blank=True)
    unsubscribe_reason = models.CharField(max_length=100, choices=UNSUBSCRIBE_REASONS, blank=True)
    gdpr_consent = models.BooleanField(default=False)
    gdpr_consent_date = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"Preferences for {self.subscriber.email}"
