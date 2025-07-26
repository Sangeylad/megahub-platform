from django.db import models

# Create your models here.
from django.db import models
import uuid

# Choices
CONDITION_TYPES = [
    ('field_value', 'Field Value'),
    ('list_membership', 'List Membership'),
    ('tag_presence', 'Tag Presence'),
    ('email_engagement', 'Email Engagement'),
    ('date_comparison', 'Date Comparison'),
    ('custom_field', 'Custom Field'),
]

OPERATORS = [
    ('equals', 'Equals'),
    ('not_equals', 'Not Equals'),
    ('contains', 'Contains'),
    ('not_contains', 'Not Contains'),
    ('greater_than', 'Greater Than'),
    ('less_than', 'Less Than'),
    ('exists', 'Exists'),
    ('not_exists', 'Not Exists'),
]

class AutomationCondition(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    automation = models.ForeignKey('mailing_automations_core.Automation', on_delete=models.CASCADE, related_name='conditions')
    action = models.ForeignKey('mailing_automations_actions.AutomationAction', on_delete=models.CASCADE, null=True, blank=True)
    condition_name = models.CharField(max_length=100)
    condition_type = models.CharField(max_length=30, choices=CONDITION_TYPES)
    operator = models.CharField(max_length=20, choices=OPERATORS)
    field_name = models.CharField(max_length=100)
    comparison_value = models.CharField(max_length=255, blank=True)
    logical_operator = models.CharField(max_length=10, default='AND')  # AND, OR
    is_active = models.BooleanField(default=True)
    evaluation_count = models.IntegerField(default=0)
    true_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.condition_name} - {self.automation.name}"
