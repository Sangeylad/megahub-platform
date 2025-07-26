from django.db import models

# Create your models here.
from django.db import models
from common.models import TimestampedMixin
import uuid

# Choices
REQUEST_METHODS = [
    ('GET', 'GET'),
    ('POST', 'POST'),
    ('PUT', 'PUT'),
    ('PATCH', 'PATCH'),
    ('DELETE', 'DELETE'),
]

class APIEndpoint(TimestampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    integration = models.ForeignKey('mailing_integrations_core.Integration', on_delete=models.CASCADE, related_name='endpoints')
    name = models.CharField(max_length=255)
    endpoint_url = models.URLField()
    method = models.CharField(max_length=10, choices=REQUEST_METHODS, default='POST')
    headers = models.JSONField(default=dict)
    authentication = models.JSONField(default=dict)
    request_template = models.JSONField(default=dict)
    response_mapping = models.JSONField(default=dict)
    timeout_seconds = models.IntegerField(default=30)
    retry_attempts = models.IntegerField(default=3)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.method} {self.endpoint_url}"

class APICall(TimestampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    endpoint = models.ForeignKey(APIEndpoint, on_delete=models.CASCADE, related_name='calls')
    request_data = models.JSONField(default=dict)
    response_status = models.IntegerField(null=True, blank=True)
    response_data = models.JSONField(default=dict)
    execution_time_ms = models.IntegerField(default=0)
    success = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    retry_count = models.IntegerField(default=0)

    def __str__(self):
        return f"API Call to {self.endpoint.name} - {self.response_status}"
