from django.db import models

# Create your models here.
from django.db import models
from common.models import TimestampedMixin
import uuid

class BrandingConfig(TimestampedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brand = models.OneToOneField('brands_core.Brand', on_delete=models.CASCADE)
    brand_name = models.CharField(max_length=255)
    brand_logo = models.ImageField(upload_to='branding/logos/', null=True, blank=True)
    primary_color = models.CharField(max_length=7, default='#000000')  # Hex color
    secondary_color = models.CharField(max_length=7, default='#ffffff')  # Hex color
    font_family = models.CharField(max_length=100, default='Arial')
    email_footer = models.TextField(blank=True)
    social_links = models.JSONField(default=dict)
    default_css = models.TextField(blank=True)
    header_template = models.TextField(blank=True)
    footer_template = models.TextField(blank=True)
    unsubscribe_page_url = models.URLField(blank=True)
    preference_center_url = models.URLField(blank=True)

    def __str__(self):
        return f"Branding for {self.brand.name}"
