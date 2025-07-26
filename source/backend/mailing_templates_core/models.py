from django.db import models

# Create your models here.
from django.db import models
from common.models import TimestampedMixin
import uuid

# Choices
TEMPLATE_CATEGORIES = [
    ('newsletter', 'Newsletter'),
    ('promotional', 'Promotional'),
    ('transactional', 'Transactional'),
    ('welcome', 'Welcome'),
    ('reengagement', 'Re-engagement'),
    ('abandoned_cart', 'Abandoned Cart'),
    ('event', 'Event'),
    ('announcement', 'Announcement'),
]

TEMPLATE_STATUSES = [
    ('draft', 'Draft'),
    ('active', 'Active'),
    ('archived', 'Archived'),
]

class EmailTemplate(TimestampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=30, choices=TEMPLATE_CATEGORIES, default='newsletter')
    status = models.CharField(max_length=20, choices=TEMPLATE_STATUSES, default='draft')
    brand = models.ForeignKey('brands_core.Brand', on_delete=models.CASCADE)
    created_by = models.ForeignKey('users_core.CustomUser', on_delete=models.CASCADE)
    html_content = models.TextField()
    text_content = models.TextField(blank=True)
    design_config = models.JSONField(default=dict)
    variables = models.JSONField(default=list)
    preview_image = models.ImageField(upload_to='templates/previews/', null=True, blank=True)
    is_favorite = models.BooleanField(default=False)
    usage_count = models.IntegerField(default=0)
    tags = models.JSONField(default=list)
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = [['name', 'brand']]
        indexes = [
            models.Index(fields=['category', 'brand']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.name} ({self.brand.name})"
