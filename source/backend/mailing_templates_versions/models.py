from django.db import models

# Create your models here.
from django.db import models
from common.models import TimestampedMixin
import uuid

# Choices
VERSION_STATUSES = [
    ('draft', 'Draft'),
    ('pending_approval', 'Pending Approval'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('archived', 'Archived'),
]

class TemplateVersion(TimestampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey('mailing_templates_core.EmailTemplate', on_delete=models.CASCADE)
    version_number = models.CharField(max_length=20)
    version_status = models.CharField(max_length=20, choices=VERSION_STATUSES, default='draft')
    html_content = models.TextField()
    text_content = models.TextField(blank=True)
    change_summary = models.TextField(blank=True)
    created_by = models.ForeignKey('users_core.CustomUser', on_delete=models.CASCADE, related_name='template_versions_created')
    approved_by = models.ForeignKey('users_core.CustomUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='template_versions_approved')
    approved_at = models.DateTimeField(null=True, blank=True)
    is_current = models.BooleanField(default=False)

    class Meta:
        unique_together = [['template', 'version_number']]

    def __str__(self):
        return f"{self.template.name} v{self.version_number}"
