from django.db import models

# Create your models here.
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from common.models import TimestampedMixin
import uuid

# Choices
CAMPAIGN_TYPES = [
    ('newsletter', 'Newsletter'),
    ('promotional', 'Promotional'),
    ('announcement', 'Announcement'),
    ('product_update', 'Product Update'),
    ('event', 'Event'),
    ('welcome', 'Welcome'),
    ('nurturing', 'Nurturing'),
    ('reengagement', 'Re-engagement'),
    ('transactional', 'Transactional'),
    ('automation', 'Automation'),
]

CAMPAIGN_STATUSES = [
    ('draft', 'Draft'),
    ('scheduled', 'Scheduled'),
    ('sending', 'Sending'),
    ('sent', 'Sent'),
    ('paused', 'Paused'),
    ('cancelled', 'Cancelled'),
    ('failed', 'Failed'),
]

SEND_TIME_OPTIMIZATION = [
    ('immediate', 'Send Immediately'),
    ('time_zone', 'Optimize by Time Zone'),
    ('engagement', 'Optimize by Engagement'),
    ('send_time', 'Send Time Optimization'),
]

class Campaign(TimestampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    subject_line = models.CharField(max_length=300)
    preview_text = models.CharField(max_length=150, blank=True)
    campaign_type = models.CharField(max_length=30, choices=CAMPAIGN_TYPES, default='newsletter')
    status = models.CharField(max_length=20, choices=CAMPAIGN_STATUSES, default='draft')
    brand = models.ForeignKey('brands_core.Brand', on_delete=models.CASCADE)
    created_by = models.ForeignKey('users_core.CustomUser', on_delete=models.CASCADE)
    template = models.ForeignKey(
        'mailing_templates_core.EmailTemplate', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    target_lists = models.ManyToManyField(
        'mailing_lists_core.MailingList', 
        blank=True,
        through='CampaignList'
    )
    target_segments = models.ManyToManyField(
        'mailing_lists_segments.ListSegment', 
        blank=True
    )
    html_content = models.TextField(blank=True)
    text_content = models.TextField(blank=True)
    from_name = models.CharField(max_length=100)
    from_email = models.EmailField()
    reply_to_email = models.EmailField(blank=True)
    send_time_optimization = models.CharField(
        max_length=20, 
        choices=SEND_TIME_OPTIMIZATION, 
        default='immediate'
    )
    scheduled_send_time = models.DateTimeField(null=True, blank=True)
    ab_test_enabled = models.BooleanField(default=False)
    ab_test_config = models.JSONField(default=dict)
    tags = models.JSONField(default=list)
    total_recipients = models.IntegerField(default=0)
    emails_sent = models.IntegerField(default=0)
    emails_delivered = models.IntegerField(default=0)
    emails_opened = models.IntegerField(default=0)
    emails_clicked = models.IntegerField(default=0)
    emails_bounced = models.IntegerField(default=0)
    emails_unsubscribed = models.IntegerField(default=0)
    open_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=4, 
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    click_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=4, 
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    sent_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = [['name', 'brand']]
        indexes = [
            models.Index(fields=['status', 'brand']),
            models.Index(fields=['campaign_type']),
            models.Index(fields=['sent_at']),
        ]

    def __str__(self):
        return f"{self.name} ({self.brand.name})"

class CampaignList(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    mailing_list = models.ForeignKey('mailing_lists_core.MailingList', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    recipients_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.campaign.name} - {self.mailing_list.name}"
