from django.db import models

# Create your models here.
from django.db import models
import uuid

# Choices
BOUNCE_TYPES = [
    ('hard', 'Hard'),
    ('soft', 'Soft'),
    ('block', 'Block'),
    ('invalid', 'Invalid'),
    ('unknown', 'Unknown'),
]

BOUNCE_SUBTYPES = [
    ('mailbox_full', 'Mailbox Full'),
    ('mailbox_not_found', 'Mailbox Not Found'),
    ('content_rejected', 'Content Rejected'),
    ('policy_violation', 'Policy Violation'),
    ('reputation_issue', 'Reputation Issue'),
    ('authentication_failed', 'Authentication Failed'),
    ('size_limit_exceeded', 'Size Limit Exceeded'),
    ('temporary_failure', 'Temporary Failure'),
    ('unknown', 'Unknown'),
]

BOUNCE_ACTIONS = [
    ('none', 'None'),
    ('suppressed', 'Suppressed'),
    ('flagged', 'Flagged'),
    ('retry', 'Retry'),
]

class BounceHandling(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email_event = models.OneToOneField('mailing_analytics_core.EmailEvent', on_delete=models.CASCADE)
    bounce_type = models.CharField(max_length=30, choices=BOUNCE_TYPES)
    bounce_subtype = models.CharField(max_length=50, choices=BOUNCE_SUBTYPES, blank=True)
    smtp_code = models.CharField(max_length=10, blank=True)
    smtp_message = models.TextField(blank=True)
    bounce_category = models.CharField(max_length=30, blank=True)
    action_taken = models.CharField(max_length=30, choices=BOUNCE_ACTIONS, default='none')
    retry_count = models.IntegerField(default=0)
    will_retry = models.BooleanField(default=False)
    next_retry = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Bounce: {self.email_event.email_address} - {self.bounce_type}"
