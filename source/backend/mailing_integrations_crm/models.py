from django.db import models

# Create your models here.
from django.db import models
from common.models import TimestampedMixin
import uuid

# Choices
SYNC_DIRECTIONS = [
    ('bidirectional', 'Bidirectional'),
    ('crm_to_mailing', 'CRM to Mailing'),
    ('mailing_to_crm', 'Mailing to CRM'),
]

SYNC_STATUSES = [
    ('pending', 'Pending'),
    ('in_progress', 'In Progress'),
    ('completed', 'Completed'),
    ('failed', 'Failed'),
]

class CRMSync(TimestampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    integration = models.OneToOneField('mailing_integrations_core.Integration', on_delete=models.CASCADE)
    sync_direction = models.CharField(max_length=30, choices=SYNC_DIRECTIONS, default='bidirectional')
    field_mapping = models.JSONField(default=dict)
    sync_rules = models.JSONField(default=dict)
    auto_sync_enabled = models.BooleanField(default=True)
    sync_interval_hours = models.IntegerField(default=24)
    last_successful_sync = models.DateTimeField(null=True, blank=True)
    total_contacts_synced = models.IntegerField(default=0)
    failed_sync_count = models.IntegerField(default=0)

    def __str__(self):
        return f"CRM Sync for {self.integration.name}"

class SyncHistory(TimestampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    crm_sync = models.ForeignKey(CRMSync, on_delete=models.CASCADE, related_name='sync_history')
    sync_status = models.CharField(max_length=20, choices=SYNC_STATUSES)
    contacts_processed = models.IntegerField(default=0)
    contacts_created = models.IntegerField(default=0)
    contacts_updated = models.IntegerField(default=0)
    contacts_failed = models.IntegerField(default=0)
    sync_duration_seconds = models.IntegerField(default=0)
    error_details = models.JSONField(default=dict)
    started_at = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Sync {self.crm_sync.integration.name} - {self.sync_status}"
