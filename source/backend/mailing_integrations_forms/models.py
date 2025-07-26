from django.db import models

# Create your models here.
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from common.models import TimestampedMixin
import uuid

# Choices
FORM_TYPES = [
    ('subscription', 'Subscription'),
    ('lead_generation', 'Lead Generation'),
    ('contact', 'Contact'),
    ('newsletter', 'Newsletter'),
    ('download', 'Download'),
    ('webinar', 'Webinar'),
    ('custom', 'Custom'),
]

class FormIntegration(TimestampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    form_type = models.CharField(max_length=30, choices=FORM_TYPES)
    brand = models.ForeignKey('brands_core.Brand', on_delete=models.CASCADE)
    target_list = models.ForeignKey('mailing_lists_core.MailingList', on_delete=models.SET_NULL, null=True, blank=True)
    double_optin_required = models.BooleanField(default=True)
    confirmation_template = models.ForeignKey('mailing_templates_core.EmailTemplate', on_delete=models.SET_NULL, null=True, blank=True)
    redirect_url = models.URLField(blank=True)
    success_message = models.TextField(blank=True)
    field_mapping = models.JSONField(default=dict)
    custom_fields = models.JSONField(default=list)
    embed_code = models.TextField(blank=True)
    submissions_count = models.IntegerField(default=0)
    conversion_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=4, 
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Form: {self.name} ({self.form_type})"

class FormSubmission(TimestampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    form = models.ForeignKey(FormIntegration, on_delete=models.CASCADE, related_name='submissions')
    email = models.EmailField()
    form_data = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    processed = models.BooleanField(default=False)
    subscriber_created = models.ForeignKey('mailing_contacts_core.EmailSubscriber', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Submission: {self.email} to {self.form.name}"
