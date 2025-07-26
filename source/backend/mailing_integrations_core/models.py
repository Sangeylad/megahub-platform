from django.db import models

# Create your models here.
from django.db import models
from common.models import TimestampedMixin
import uuid

# Choices
INTEGRATION_TYPES = [
    ('crm', 'CRM'),
    ('ecommerce', 'E-commerce'),
    ('webhook', 'Webhook'),
    ('api', 'API'),
    ('zapier', 'Zapier'),
    ('wordpress', 'WordPress'),
    ('landing_page', 'Landing Page'),
    ('form_builder', 'Form Builder'),
]

INTEGRATION_STATUSES = [
    ('active', 'Active'),
    ('inactive', 'Inactive'),
    ('error', 'Error'),
    ('pending', 'Pending'),
]

class Integration(TimestampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    integration_type = models.CharField(max_length=30, choices=INTEGRATION_TYPES)
    status = models.CharField(max_length=20, choices=INTEGRATION_STATUSES, default='active')
    brand = models.ForeignKey('brands_core.Brand', on_delete=models.CASCADE)
    created_by = models.ForeignKey('users_core.CustomUser', on_delete=models.CASCADE)
    configuration = models.JSONField(default=dict)
    api_endpoint = models.URLField(blank=True)
    api_key = models.CharField(max_length=255, blank=True)
    webhook_url = models.URLField(blank=True)
    sync_frequency = models.CharField(max_length=20, default='real_time')
    last_sync = models.DateTimeField(null=True, blank=True)
    sync_status = models.CharField(max_length=20, default='pending')
    error_log = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.integration_type})"

class IntegrationLog(TimestampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    integration = models.ForeignKey(Integration, on_delete=models.CASCADE, related_name='logs')
    action = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    request_data = models.JSONField(default=dict)
    response_data = models.JSONField(default=dict)
    error_message = models.TextField(blank=True)
    execution_time_ms = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.integration.name} - {self.action} ({self.status})"
