from django.db import models

# Create your models here.
from django.db import models
from common.models import TimestampedMixin
import uuid

# Choices
LIST_TYPES = [
    ('static', 'Static'),
    ('dynamic', 'Dynamic'),
    ('smart', 'Smart'),
]

SUBSCRIBER_SOURCES = [
    ('manual', 'Manual'),
    ('import', 'Import'),
    ('api', 'API'),
    ('form', 'Form'),
    ('integration', 'Integration'),
    ('automation', 'Automation'),
]

class MailingList(TimestampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    list_type = models.CharField(max_length=30, choices=LIST_TYPES, default='static')
    brand = models.ForeignKey('brands_core.Brand', on_delete=models.CASCADE)
    created_by = models.ForeignKey('users_core.CustomUser', on_delete=models.CASCADE)
    subscribers = models.ManyToManyField(
        'mailing_contacts_core.EmailSubscriber',
        through='ListMembership',
        blank=True
    )
    subscriber_count = models.IntegerField(default=0)
    is_public = models.BooleanField(default=False)
    tags = models.JSONField(default=list)

    class Meta:
        unique_together = [['name', 'brand']]
        indexes = [
            models.Index(fields=['list_type', 'brand']),
        ]

    def __str__(self):
        return f"{self.name} ({self.brand.name})"

class ListMembership(TimestampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mailing_list = models.ForeignKey(MailingList, on_delete=models.CASCADE)
    subscriber = models.ForeignKey('mailing_contacts_core.EmailSubscriber', on_delete=models.CASCADE)
    added_by = models.ForeignKey('users_core.CustomUser', on_delete=models.SET_NULL, null=True, blank=True)
    subscription_source = models.CharField(max_length=50, choices=SUBSCRIBER_SOURCES, default='manual')
    added_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = [['mailing_list', 'subscriber']]

    def __str__(self):
        return f"{self.subscriber.email} in {self.mailing_list.name}"
