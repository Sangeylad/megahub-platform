from django.db import models

# Create your models here.
from django.db import models
from common.models import TimestampedMixin
import uuid

# Choices
REPORT_TYPES = [
    ('campaign_performance', 'Campaign Performance'),
    ('subscriber_engagement', 'Subscriber Engagement'),
    ('list_growth', 'List Growth'),
    ('automation_performance', 'Automation Performance'),
    ('deliverability', 'Deliverability'),
    ('roi_analysis', 'ROI Analysis'),
    ('custom', 'Custom'),
]

SCHEDULE_FREQUENCIES = [
    ('daily', 'Daily'),
    ('weekly', 'Weekly'),
    ('monthly', 'Monthly'),
    ('quarterly', 'Quarterly'),
]

class AnalyticsReport(TimestampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
    brand = models.ForeignKey('brands_core.Brand', on_delete=models.CASCADE)
    created_by = models.ForeignKey('users_core.CustomUser', on_delete=models.CASCADE)
    filters = models.JSONField(default=dict)
    date_range_start = models.DateTimeField()
    date_range_end = models.DateTimeField()
    report_data = models.JSONField(default=dict)
    is_scheduled = models.BooleanField(default=False)
    schedule_frequency = models.CharField(max_length=20, choices=SCHEDULE_FREQUENCIES, blank=True)
    next_generation = models.DateTimeField(null=True, blank=True)
    file_export = models.FileField(upload_to='reports/', null=True, blank=True)

    def __str__(self):
        return f"Report: {self.name}"
from django.db import models
from common.models import TimestampedMixin
import uuid

# Choices
REPORT_TYPES = [
    ('campaign_performance', 'Campaign Performance'),
    ('subscriber_engagement', 'Subscriber Engagement'),
    ('list_growth', 'List Growth'),
    ('automation_performance', 'Automation Performance'),
    ('deliverability', 'Deliverability'),
    ('roi_analysis', 'ROI Analysis'),
    ('custom', 'Custom'),
]

SCHEDULE_FREQUENCIES = [
    ('daily', 'Daily'),
    ('weekly', 'Weekly'),
    ('monthly', 'Monthly'),
    ('quarterly', 'Quarterly'),
]

class AnalyticsReport(TimestampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
    brand = models.ForeignKey('brands_core.Brand', on_delete=models.CASCADE)
    created_by = models.ForeignKey('users_core.CustomUser', on_delete=models.CASCADE)
    filters = models.JSONField(default=dict)
    date_range_start = models.DateTimeField()
    date_range_end = models.DateTimeField()
    report_data = models.JSONField(default=dict)
    is_scheduled = models.BooleanField(default=False)
    schedule_frequency = models.CharField(max_length=20, choices=SCHEDULE_FREQUENCIES, blank=True)
    next_generation = models.DateTimeField(null=True, blank=True)
    file_export = models.FileField(upload_to='reports/', null=True, blank=True)

    def __str__(self):
        return f"Report: {self.name}"
