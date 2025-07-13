# backend/ai_templates_core/models/template_models.py

from django.db import models
from common.models.mixins import TimestampedMixin

class TemplateType(TimestampedMixin):
    """Types de templates IA"""
    name = models.CharField(max_length=100, unique=True)  # website, blog, social, email
    display_name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'template_type'
        ordering = ['name']
    
    def __str__(self):
        return self.display_name

class BrandTemplateConfig(TimestampedMixin):
    """Configuration templates par brand"""
    brand = models.OneToOneField('brands_core.Brand', on_delete=models.CASCADE, related_name='template_config')
    max_templates_per_type = models.PositiveIntegerField(default=50)
    max_variables_per_template = models.PositiveIntegerField(default=20)
    allow_custom_templates = models.BooleanField(default=True)
    default_template_style = models.CharField(max_length=100, default='professional')
    
    class Meta:
        db_table = 'brand_template_config'
    
    def __str__(self):
        return f"Config templates - {self.brand.name}"

class BaseTemplate(TimestampedMixin):
    """Modèle de base pour tous les templates IA"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    template_type = models.ForeignKey(TemplateType, on_delete=models.CASCADE, related_name='templates')
    brand = models.ForeignKey('brands_core.Brand', on_delete=models.CASCADE, related_name='ai_templates')
    prompt_content = models.TextField(help_text="Contenu du prompt avec variables {{variable}}")
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=False, help_text="Template partageable entre brands")
    created_by = models.ForeignKey('users_core.CustomUser', on_delete=models.SET_NULL, null=True, related_name='authored_ai_templates')
    
    class Meta:
        db_table = 'base_template'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['brand', 'template_type']),
            models.Index(fields=['is_active', 'is_public'])
        ]
        unique_together = ['brand', 'name', 'template_type']
    
    def __str__(self):
        return f"{self.name} ({self.template_type.display_name})"
