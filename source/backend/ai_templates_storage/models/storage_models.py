# backend/ai_templates_storage/models/storage_models.py

from django.db import models
from common.models.mixins import TimestampedMixin

class TemplateVariable(TimestampedMixin):
    """Variables utilisables dans les templates"""
    name = models.CharField(max_length=100)  # brand_name, target_keyword, etc.
    display_name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    variable_type = models.CharField(max_length=50, choices=[
        ('brand', 'Brand Data'),
        ('seo', 'SEO Data'), 
        ('user', 'User Input'),
        ('system', 'System Generated')
    ], default='user')
    default_value = models.CharField(max_length=500, blank=True)
    is_required = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'template_variable'
        ordering = ['name']
        unique_together = ['name']
    
    def __str__(self):
        return f"{{{{{self.name}}}}}"

class TemplateVersion(TimestampedMixin):
    """Historique des versions de templates"""
    template = models.ForeignKey('ai_templates_core.BaseTemplate', on_delete=models.CASCADE, related_name='versions')
    version_number = models.PositiveIntegerField()
    prompt_content = models.TextField()
    changelog = models.TextField(blank=True, help_text="Description des changements")
    is_current = models.BooleanField(default=False)
    created_by = models.ForeignKey('users_core.CustomUser', on_delete=models.SET_NULL, null=True, related_name='authored_template_versions')
    
    class Meta:
        db_table = 'template_version'
        ordering = ['-version_number']
        indexes = [
            models.Index(fields=['template', 'is_current'])
        ]
        unique_together = ['template', 'version_number']
    
    def __str__(self):
        return f"{self.template.name} v{self.version_number}"
    
    def save(self, *args, **kwargs):
        """Auto-incrémente version_number"""
        if not self.version_number:
            last_version = TemplateVersion.objects.filter(template=self.template).order_by('-version_number').first()
            self.version_number = (last_version.version_number + 1) if last_version else 1
        super().save(*args, **kwargs)
