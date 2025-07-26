from django.db import models

# Create your models here.
from django.db import models
from common.models import TimestampedMixin
import uuid

# Choices
USER_ROLES = [
    ('viewer', 'Viewer'),
    ('editor', 'Editor'),
    ('manager', 'Manager'),
    ('admin', 'Admin'),
]

class UserPermissions(TimestampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('users_core.CustomUser', on_delete=models.CASCADE)
    brand = models.ForeignKey('brands_core.Brand', on_delete=models.CASCADE)
    role = models.CharField(max_length=30, choices=USER_ROLES, default='viewer')
    can_create_campaigns = models.BooleanField(default=False)
    can_edit_campaigns = models.BooleanField(default=False)
    can_send_campaigns = models.BooleanField(default=False)
    can_manage_lists = models.BooleanField(default=False)
    can_manage_templates = models.BooleanField(default=False)
    can_view_analytics = models.BooleanField(default=True)
    can_export_data = models.BooleanField(default=False)
    can_manage_integrations = models.BooleanField(default=False)
    can_manage_settings = models.BooleanField(default=False)
    send_limit_per_day = models.IntegerField(null=True, blank=True)
    allowed_features = models.JSONField(default=list)

    class Meta:
        unique_together = [['user', 'brand']]

    def __str__(self):
        return f"{self.user.email} - {self.brand.name} ({self.role})"
