from django.db import models

# Create your models here.
from django.db import models
from common.models import TimestampedMixin
import uuid

# Choices
ACTION_TYPES = [
    ('send_email', 'Send Email'),
    ('add_to_list', 'Add to List'),
    ('remove_from_list', 'Remove from List'),
    ('add_tag', 'Add Tag'),
    ('remove_tag', 'Remove Tag'),
    ('update_field', 'Update Field'),
    ('wait', 'Wait'),
    ('webhook', 'Webhook'),
    ('api_call', 'API Call'),
    ('conditional_split', 'Conditional Split'),
]

class AutomationAction(TimestampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    automation = models.ForeignKey('mailing_automations_core.Automation', on_delete=models.CASCADE, related_name='actions')
    action_name = models.CharField(max_length=100)
    action_type = models.CharField(max_length=30, choices=ACTION_TYPES)
    action_order = models.IntegerField(default=0)
    action_config = models.JSONField(default=dict)
    parent_action = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    execution_count = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    failure_count = models.IntegerField(default=0)
    last_executed = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['action_order']

    def __str__(self):
        return f"{self.action_name} - {self.automation.name}"
