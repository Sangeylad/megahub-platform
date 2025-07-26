from django.db import models

# Create your models here.
from django.db import models
import uuid

# Choices
DEVICE_TYPES = [
    ('mobile', 'Mobile'),
    ('desktop', 'Desktop'),
    ('tablet', 'Tablet'),
    ('smart_tv', 'Smart TV'),
    ('wearable', 'Wearable'),
    ('other', 'Other'),
]

EMAIL_CLIENTS = [
    ('gmail', 'Gmail'),
    ('outlook', 'Outlook'),
    ('apple_mail', 'Apple Mail'),
    ('yahoo', 'Yahoo Mail'),
    ('thunderbird', 'Thunderbird'),
    ('webmail', 'Webmail'),
    ('mobile_app', 'Mobile App'),
    ('other', 'Other'),
]

OPERATING_SYSTEMS = [
    ('windows', 'Windows'),
    ('macos', 'macOS'),
    ('ios', 'iOS'),
    ('android', 'Android'),
    ('linux', 'Linux'),
    ('other', 'Other'),
]

class EmailOpen(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email_event = models.OneToOneField('mailing_analytics_core.EmailEvent', on_delete=models.CASCADE)
    is_unique = models.BooleanField(default=True)
    open_count = models.IntegerField(default=1)
    email_client = models.CharField(max_length=100, choices=EMAIL_CLIENTS, blank=True)
    device_type = models.CharField(max_length=30, choices=DEVICE_TYPES, blank=True)
    operating_system = models.CharField(max_length=50, choices=OPERATING_SYSTEMS, blank=True)
    location_country = models.CharField(max_length=100, blank=True)
    location_region = models.CharField(max_length=100, blank=True)
    location_city = models.CharField(max_length=100, blank=True)
    timezone = models.CharField(max_length=50, blank=True)
    forwarded = models.BooleanField(default=False)

    def __str__(self):
        return f"Open: {self.email_event.email_address}"
