from django.db import models

# Create your models here.
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from common.models import TimestampedMixin
import uuid

# Choices
WARMUP_TEMPLATE_TYPES = [
    ('business', 'Business'),
    ('conversation', 'Conversation'),
    ('reply', 'Reply'),
    ('introduction', 'Introduction'),
]

USAGE_FREQUENCIES = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
]

SENTIMENT_TYPES = [
    ('positive', 'Positive'),
    ('neutral', 'Neutral'),
    ('professional', 'Professional'),
]

class IPWarming(TimestampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    config = models.ForeignKey('mailing_deliverability_core.DeliverabilityConfig', on_delete=models.CASCADE)
    campaign_name = models.CharField(max_length=255)
    target_ip = models.GenericIPAddressField()
    target_domain = models.CharField(max_length=255)
    warmup_status = models.CharField(max_length=30, default='active')
    start_volume = models.IntegerField(default=50)
    current_volume = models.IntegerField(default=50)
    target_volume = models.IntegerField(default=10000)
    daily_increase_percent = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=10,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    warmup_duration_days = models.IntegerField(default=30)
    current_day = models.IntegerField(default=1)
    reputation_threshold = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=80,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    bounce_rate_threshold = models.DecimalField(
        max_digits=5, 
        decimal_places=4, 
        default=0.05,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    algorithm_config = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"IP Warming: {self.campaign_name}"

class WarmupPartner(TimestampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    domain = models.CharField(max_length=255)
    provider = models.CharField(max_length=100)
    trust_score = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=50,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    engagement_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=4, 
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    preferred_send_times = models.JSONField(default=list)
    timezone = models.CharField(max_length=50, default='Europe/Paris')
    language = models.CharField(max_length=10, default='fr')
    is_active = models.BooleanField(default=True)
    last_email_sent = models.DateTimeField(null=True, blank=True)
    total_emails_sent = models.IntegerField(default=0)
    total_emails_opened = models.IntegerField(default=0)
    total_emails_replied = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.email})"

class WarmupEmail(TimestampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    warming_campaign = models.ForeignKey(IPWarming, on_delete=models.CASCADE, related_name='warmup_emails')
    partner = models.ForeignKey(WarmupPartner, on_delete=models.CASCADE)
    subject_line = models.CharField(max_length=300)
    content = models.TextField()
    sent_at = models.DateTimeField()
    opened_at = models.DateTimeField(null=True, blank=True)
    clicked_at = models.DateTimeField(null=True, blank=True)
    replied_at = models.DateTimeField(null=True, blank=True)
    engagement_score = models.DecimalField(
        max_digits=5, 
        decimal_places=4, 
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    template_used = models.ForeignKey('WarmupTemplate', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Warmup Email to {self.partner.email}"

class WarmupMetrics(TimestampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    warming_campaign = models.ForeignKey(IPWarming, on_delete=models.CASCADE, related_name='metrics')
    date = models.DateField()
    emails_sent = models.IntegerField(default=0)
    emails_delivered = models.IntegerField(default=0)
    emails_opened = models.IntegerField(default=0)
    emails_clicked = models.IntegerField(default=0)
    emails_replied = models.IntegerField(default=0)
    emails_bounced = models.IntegerField(default=0)
    reputation_score = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    volume_increase_percent = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(-100), MaxValueValidator(100)]
    )
    algorithm_adjustment = models.JSONField(default=dict)
    warning_flags = models.JSONField(default=list)

    class Meta:
        unique_together = [['warming_campaign', 'date']]

    def __str__(self):
        return f"Metrics for {self.warming_campaign.campaign_name} - {self.date}"

class WarmupTemplate(TimestampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    template_type = models.CharField(max_length=30, choices=WARMUP_TEMPLATE_TYPES)
    subject_templates = models.JSONField()
    content_templates = models.JSONField()
    variables = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    usage_frequency = models.CharField(max_length=20, choices=USAGE_FREQUENCIES, default='medium')
    language = models.CharField(max_length=10, default='fr')
    sentiment = models.CharField(max_length=20, choices=SENTIMENT_TYPES, default='neutral')

    def __str__(self):
        return f"Warmup Template: {self.name}"
