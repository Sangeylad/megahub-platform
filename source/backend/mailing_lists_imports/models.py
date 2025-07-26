from django.db import models

# Create your models here.
from django.db import models
from common.models import TimestampedMixin
import uuid

# Choices
FILE_FORMATS = [
    ('csv', 'CSV'),
    ('xlsx', 'Excel'),
    ('json', 'JSON'),
    ('txt', 'Text'),
]

IMPORT_STATUSES = [
    ('pending', 'Pending'),
    ('processing', 'Processing'),
    ('completed', 'Completed'),
    ('failed', 'Failed'),
    ('cancelled', 'Cancelled'),
]

class ListImport(TimestampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    import_file = models.FileField(upload_to='imports/')
    file_format = models.CharField(max_length=20, choices=FILE_FORMATS, default='csv')
    import_status = models.CharField(max_length=30, choices=IMPORT_STATUSES, default='pending')
    target_list = models.ForeignKey('mailing_lists_core.MailingList', on_delete=models.SET_NULL, null=True, blank=True)
    create_new_list = models.BooleanField(default=False)
    new_list_name = models.CharField(max_length=255, blank=True)
    column_mapping = models.JSONField(default=dict)
    import_options = models.JSONField(default=dict)
    total_rows = models.IntegerField(default=0)
    processed_rows = models.IntegerField(default=0)
    successful_imports = models.IntegerField(default=0)
    failed_imports = models.IntegerField(default=0)
    duplicate_count = models.IntegerField(default=0)
    error_log = models.TextField(blank=True)
    imported_by = models.ForeignKey('users_core.CustomUser', on_delete=models.CASCADE)
    brand = models.ForeignKey('brands_core.Brand', on_delete=models.CASCADE)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Import: {self.name}"
