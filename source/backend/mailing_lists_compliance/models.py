from django.db import models

# Create your models here.
from django.db import models
from common.models import TimestampedMixin
import uuid

# Choices
SUPPRESSION_TYPES = [
    ('unsubscribe', 'Unsubscribe'),
    ('bounce', 'Bounce'),
    ('complaint', 'Complaint'),
    ('manual', 'Manual'),
    ('global', 'Global'),
]

class SuppressionList(TimestampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    suppression_type = models.CharField(max_length=30, choices=SUPPRESSION_TYPES)
    reason = models.CharField(max_length=100, blank=True)
    brand = models.ForeignKey('brands_core.Brand', on_delete=models.SET_NULL, null=True, blank=True)
    is_global = models.BooleanField(default=False)
    added_by = models.ForeignKey('users_core.CustomUser', on_delete=models.SET_NULL, null=True, blank=True)
    source_campaign = models.ForeignKey('mailing_campaigns_core.Campaign', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Suppressed: {self.email}"
