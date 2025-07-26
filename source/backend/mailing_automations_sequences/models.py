from django.db import models

# Create your models here.
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from common.models import TimestampedMixin
import uuid

# Choices
SEQUENCE_TYPES = [
    ('linear', 'Linear'),
    ('conditional', 'Conditional'),
    ('parallel', 'Parallel'),
]

DELAY_UNITS = [
    ('hours', 'Hours'),
    ('days', 'Days'),
    ('weeks', 'Weeks'),
]

class AutomationSequence(TimestampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    automation = models.OneToOneField('mailing_automations_core.Automation', on_delete=models.CASCADE)
    sequence_type = models.CharField(max_length=30, choices=SEQUENCE_TYPES, default='linear')
    total_emails = models.IntegerField(default=0)
    average_duration_days = models.IntegerField(default=0)
    completion_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=4, 
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    drop_off_analysis = models.JSONField(default=dict)

    def __str__(self):
        return f"Sequence for {self.automation.name}"

class SequenceEmail(TimestampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sequence = models.ForeignKey(AutomationSequence, on_delete=models.CASCADE, related_name='emails')
    email_order = models.IntegerField()
    email_name = models.CharField(max_length=255)
    template = models.ForeignKey('mailing_templates_core.EmailTemplate', on_delete=models.SET_NULL, null=True, blank=True)
    delay_from_previous = models.IntegerField(default=1)
    delay_unit = models.CharField(max_length=20, choices=DELAY_UNITS, default='days')
    send_conditions = models.JSONField(default=dict)
    sent_count = models.IntegerField(default=0)
    open_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=4, 
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    click_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=4, 
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )

    class Meta:
        unique_together = [['sequence', 'email_order']]
        ordering = ['email_order']

    def __str__(self):
        return f"{self.email_name} (#{self.email_order})"
