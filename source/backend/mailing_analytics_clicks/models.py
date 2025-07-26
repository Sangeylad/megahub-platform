from django.db import models

# Create your models here.
from django.db import models
import uuid

class EmailClick(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email_event = models.OneToOneField('mailing_analytics_core.EmailEvent', on_delete=models.CASCADE)
    clicked_url = models.URLField()
    original_url = models.URLField()
    link_text = models.CharField(max_length=255, blank=True)
    link_position = models.CharField(max_length=50, blank=True)
    is_unique = models.BooleanField(default=True)
    click_count = models.IntegerField(default=1)
    device_type = models.CharField(max_length=30, blank=True)
    referrer = models.URLField(blank=True)

    def __str__(self):
        return f"Click: {self.email_event.email_address} -> {self.clicked_url}"
