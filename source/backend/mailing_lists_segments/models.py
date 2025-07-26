from django.db import models

# Create your models here.
from django.db import models
from common.models import TimestampedMixin
import uuid

# Choices
SEGMENT_TYPES = [
    ('static', 'Static'),
    ('dynamic', 'Dynamic'),
    ('behavioral', 'Behavioral'),
    ('demographic', 'Demographic'),
]

OPERATORS = [
    ('equals', 'Equals'),
    ('not_equals', 'Not Equals'),
    ('contains', 'Contains'),
    ('not_contains', 'Not Contains'),
    ('starts_with', 'Starts With'),
    ('ends_with', 'Ends With'),
    ('greater_than', 'Greater Than'),
    ('less_than', 'Less Than'),
    ('greater_equal', 'Greater or Equal'),
    ('less_equal', 'Less or Equal'),
    ('in', 'In'),
    ('not_in', 'Not In'),
]

class ListSegment(TimestampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    segment_type = models.CharField(max_length=30, choices=SEGMENT_TYPES, default='dynamic')
    brand = models.ForeignKey('brands_core.Brand', on_delete=models.CASCADE)
    created_by = models.ForeignKey('users_core.CustomUser', on_delete=models.CASCADE)
    conditions = models.JSONField(default=dict)
    logical_operator = models.CharField(max_length=10, default='AND')  # AND, OR
    subscribers = models.ManyToManyField('mailing_contacts_core.EmailSubscriber', blank=True)
    subscriber_count = models.IntegerField(default=0)
    last_evaluated_at = models.DateTimeField(null=True, blank=True)
    auto_update = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = [['name', 'brand']]

    def __str__(self):
        return f"{self.name} ({self.brand.name})"

class SegmentCondition(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    segment = models.ForeignKey(ListSegment, on_delete=models.CASCADE, related_name='segment_conditions')
    field_name = models.CharField(max_length=100)
    operator = models.CharField(max_length=20, choices=OPERATORS)
    value = models.CharField(max_length=255)
    logical_operator = models.CharField(max_length=10, default='AND')
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.field_name} {self.operator} {self.value}"
